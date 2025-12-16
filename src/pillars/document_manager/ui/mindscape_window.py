
from PyQt6.QtWidgets import (
    QMainWindow, QGraphicsView, QDockWidget, QMenu, QMessageBox, 
    QInputDialog, QFileDialog, QWidget, QVBoxLayout, QStackedWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QRunnable, QThreadPool, QObject, pyqtSignal
from typing import Optional, Any
from .mindscape_view import MindscapeView
from .mindscape_items import MindscapeNodeItem, MindscapeEdgeItem
from .mindscape_inspector import NodeInspectorWidget
from ..services.mindscape_service import mindscape_service_context
from ..services.document_service import document_service_context
from .document_editor_window import DocumentEditorWindow
import json
import os

from .search_results_panel import SearchResultsPanel

class MindscapeWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # ... (Central Widget Init) ...
        self.setWindowTitle("Mindscape: The Living Graph")
        self.resize(1400, 800) # Slightly wider for dock
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.view = MindscapeView()
        self.main_layout.addWidget(self.view)
        self.thread_pool: QThreadPool = QThreadPool.globalInstance() or QThreadPool()

        # Docks (Tabbed: Inspector | Search Results)
        self.dock = QDockWidget("Mindscape Tools", self)
        self.dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea)
        
        # Stacked Container
        self.stack = QStackedWidget()
        
        self.inspector = NodeInspectorWidget()
        self.search_panel = SearchResultsPanel()
        
        self.stack.addWidget(self.inspector)
        self.stack.addWidget(self.search_panel)
        
        self.dock.setWidget(self.stack) # Set stack directly as dock widget
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)
        self.dock.hide() 
        
        # Signals
        self.inspector.node_updated.connect(self._save_node_changes)
        self.inspector.edge_updated.connect(self._save_edge_changes)
        
        # Search Panel Signals
        self.search_panel.add_to_graph_requested.connect(self._add_search_result_to_graph)
        self.search_panel.open_document_requested.connect(self._open_document_by_id)
        
        # View Signals
        self.view.node_selected.connect(self._on_node_selected)
        
        self._setup_toolbar()
        self._init_graph()
        self._setup_interactions()

    @pyqtSlot(int)
    def _on_node_selected(self, node_id):
        """Handle selection to toggle between Inspector and Search Panel."""
        try:
            with mindscape_service_context() as svc:
                focus, _, _, _, _ = svc.get_local_graph(node_id)
                if not focus: return
                
                self.dock.setVisible(True)
                self.dock.raise_()
                
                if focus.type == "search_query":
                    # Show Search Panel
                    self.stack.setCurrentWidget(self.search_panel)
                    self.dock.setWindowTitle("Search Results")
                    
                    # Parse results from metadata
                    results = []
                    term = None
                    if focus.metadata_payload:
                        try:
                            data = json.loads(focus.metadata_payload)
                            if isinstance(data, list): results = data
                            elif "results" in data: 
                                results = data["results"]
                                term = data.get("term") # Extract term
                        except: pass
                    
                    self.search_panel.load_results(results, term=term or "")
                    
                else:
                    # Show Inspector
                    self.stack.setCurrentWidget(self.inspector)
                    self.dock.setWindowTitle("Inspector")
                    self.inspector.set_data(focus, "node")
                
        except Exception as e:
            print(f"Error selecting node: {e}")

    # ... (Keep existing methods: _open_edge_inspector, _save_*, _setup_toolbar, etc.)

    def _create_search_node(self):
        """Create a central node with results stored in metadata."""
        term, ok = QInputDialog.getText(self, "Create Search Node", "Enter search term:")
        if not ok or not term.strip():
            return
        
        class SearchSignals(QObject):
            finished = pyqtSignal(object, list)

        class SearchTask(QRunnable):
            def __init__(self, term, signals):
                super().__init__()
                self.term = term
                self.signals = signals

            def run(self):
                sanitized_results = []
                with document_service_context() as doc_service:
                    results = doc_service.search_documents_with_highlights(self.term, limit=50)
                for r in results:
                    clean_r = r.copy()
                    if 'created_at' in clean_r and hasattr(clean_r['created_at'], 'isoformat'):
                        clean_r['created_at'] = clean_r['created_at'].isoformat()
                    sanitized_results.append(clean_r)
                self.signals.finished.emit(self.term, sanitized_results)

        sig = SearchSignals()

        def _on_finished(term_value, sanitized_results):
            if not sanitized_results:
                QMessageBox.information(self, "No Results", f"No documents found for '{term_value}'")
                return
            with mindscape_service_context() as mind_service:
                meta = {"results": sanitized_results, "term": term_value}
                search_node = mind_service.create_node(
                    title=f"Concept: {term_value}",
                    type="search_query",
                    content=f"Search Query: '{term_value}'\nClick to see {len(sanitized_results)} results.",
                    metadata_payload=meta,
                    appearance={"shape": "hexagon", "color_override": "#8b5cf6", "textColor": "#ffffff", "borderWidth": 2}
                )

                parent_id = self.view.current_focus_id
                if not parent_id:
                    home = mind_service.get_home_node()
                    if home and home.id != search_node.id:
                        parent_id = home.id

                if parent_id:
                    mind_service.link_nodes(parent_id, search_node.id, "parent")

                self.view.load_graph(search_node.id, keep_existing=True)
                QMessageBox.information(self, "Search Complete", f"Created Concept '{term_value}'.\n{len(sanitized_results)} results initialized.")

        sig.finished.connect(_on_finished)
        self.thread_pool.start(SearchTask(term, sig))

    def _add_search_result_to_graph(self, result_data):
        """Called from Panel to materialize a document node."""
        doc_id = result_data['id']
        snippet = result_data.get('highlights', '')
        
        with mindscape_service_context() as svc:
            # 1. Check if exists
            existing = svc.find_node_by_document_id(doc_id)
            node_id = None
            
            if existing:
                node_id = existing.id
                QMessageBox.information(self, "Exists", f"'{result_data['title']}' is already in the Mindscape.")
            else:
                # 2. Create
                new_node = svc.create_node(
                    title=result_data['title'],
                    type="document",
                    content=snippet,
                    metadata_payload={"document_id": doc_id},
                    appearance={"shape": "document", "color_override": "#e0f2fe", "textColor": "#0f172a", "borderColor": "#0284c7"}
                )
                node_id = new_node.id
                
                # Link to current Focus if it is a search query?
                if self.view.current_focus_id:
                     svc.link_nodes(node_id, self.view.current_focus_id, "parent") # Doc -> Concept
            
            # 3. Load/Center
            if node_id:
                self.view.load_graph(node_id, keep_existing=True)
                
            # 4. Open and Highlight (User Request)
            highlight = result_data.get('search_term')
            self._open_document_by_id(doc_id, highlight_text=highlight)

    def _open_document_by_id(self, doc_id, highlight_text=None):
         # Just a wrapper around existing logic if possible or direct
         # We need to find if there is a node, if not, open directly?
         # _open_document_node requires a node_id.
         # Let's bypass and open directly using DocService
         with document_service_context() as doc_service:
            doc = doc_service.get_document(doc_id)
            if doc:
                self.doc_editor_Direct = DocumentEditorWindow(self) # Keep reference
                self.doc_editor_Direct.load_document_model(doc, search_term=highlight_text)
                self.doc_editor_Direct.show()
        
    def _setup_toolbar(self):
        """Build the modern toolbar."""
        from PyQt6.QtWidgets import QToolBar, QLabel
        from PyQt6.QtGui import QAction, QIcon
        
        toolbar = QToolBar("Mindscape Actions", self)
        toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        
        # Style
        # Modern Flat look
        self.setStyleSheet("""
        QToolBar {
            background-color: #1e1e1e;
            border-bottom: 2px solid #333;
            spacing: 12px;
            padding: 8px;
        }
        QToolButton {
            background-color: transparent;
            border: 1px solid #444;
            border-radius: 6px;
            padding: 6px 12px;
            color: #ddd;
            font-weight: bold;
        }
        QToolButton:hover {
            background-color: #333;
            border-color: #666;
            color: white;
        }
        QToolButton:pressed {
            background-color: #000;
        }
        """)
        
        # 1. New Thought
        new_act = QAction("New Thought", self)
        new_act.setStatusTip("Create a new root thought")
        new_act.triggered.connect(self._create_root_node)
        toolbar.addAction(new_act)
        
        # 2. Import Docs
        import_act = QAction("Import Document", self)
        import_act.setStatusTip("Import a file as a node")
        import_act.triggered.connect(lambda: self._import_documents(None))
        toolbar.addAction(import_act)
        
        # 3. Search
        search_act = QAction("Search Knowledge", self)
        search_act.setStatusTip("Search documents and create a graph")
        search_act.triggered.connect(self._create_search_node)
        toolbar.addAction(search_act)

        # 4. Save Mindscape
        save_act = QAction("Save Mindscape", self)
        save_act.setStatusTip("Export the entire mindscape to a JSON file")
        save_act.triggered.connect(self._export_mindscape)
        toolbar.addAction(save_act)

        # 5. Load Mindscape
        load_act = QAction("Load Mindscape", self)
        load_act.setStatusTip("Import a mindscape snapshot (replaces current graph)")
        load_act.triggered.connect(self._import_mindscape)
        toolbar.addAction(load_act)
        
        # Spacer
        empty = QWidget()
        empty.setFixedWidth(20)
        toolbar.addWidget(empty)
        
        # 4. Cleanse (Danger)
        cleanse_act = QAction("Cleanse Mindmap", self)
        cleanse_act.setStatusTip("Delete all nodes and edges (Irreversible)")
        cleanse_act.triggered.connect(self._cleanse_mindmap)
        
        # Find the button widget to style it specifically red
        # We add the action, then find the widget related to it? 
        # Easier: Create a specialized button widget or just rely on CSS class if accessible.
        # But QToolBar wraps actions. Let's just add it and maybe style it differently via object name?
        toolbar.addAction(cleanse_act)
        
        # Hack to style the last button red?
        # Accessing widgetForAction works if toolbar has it.
        w = toolbar.widgetForAction(cleanse_act)
        if w:
            w.setStyleSheet("""
            QToolButton {
                border: 1px solid #7f1d1d;
                color: #fca5a5;
            }
            QToolButton:hover {
                background-color: #991b1b;
                color: white;
            }
            """)

    def _cleanse_mindmap(self):
        """Wipe the database after strong confirmation."""
        reply = QMessageBox.question(
            self, "Cleanse Mindmap?",
            "WARNING: This will delete ALL nodes and edges in the Mindscape.\n\n"
            "This action cannot be undone.\n\n"
            "Are you absolutely sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                with mindscape_service_context() as svc:
                    svc.wipe_database()
                    
                scene_obj = self.view.scene()
                if scene_obj:
                    scene_obj.clear()
                self.view._items.clear()
                self.view._edges.clear()
                self.view.current_focus_id = None
                self.view.physics.clear() # IMPORTANT: Clear physics engine too
                self.view.update()
                
                QMessageBox.information(self, "Cleansed", "The Mindscape has been wiped clean.")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _open_inspector(self, node_id):
        """Manually open inspector for a specific node."""
        self.dock.show()
        self._on_node_selected(node_id)

    def _open_edge_inspector(self, edge_id):
        """Manually open inspector for a specific edge."""
        self.dock.show()
        self._on_edge_selected(edge_id)


    def _on_edge_selected(self, edge_id):
        """Fetch edge details."""
        try:
            with mindscape_service_context() as svc:
                edge = svc.get_edge(edge_id)
                self.inspector.set_data(edge, "edge")
                
        except Exception as e:
            print(f"Error fetching edge details: {e}")

    def _save_node_changes(self, data):
        """Save edits from Inspector."""
        node_id = data.get("id")
        if not node_id:
            return
            
        try:
            with mindscape_service_context() as svc:
                updated_node = svc.update_node(node_id, data)
                
            # Update Visuals immediately
            style = None
            if updated_node.appearance:
                import json
                try:
                    style = json.loads(updated_node.appearance)
                except:
                    pass
            
            # Pass both style and title (if changed)
            self.view.update_node_visual(node_id, style_dict=style, title=updated_node.title)
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def _save_edge_changes(self, data):
        """Save edge edits."""
        print(f"[Window] Saving edge changes: {data}")
        edge_id = data.get("id")
        if not edge_id: return
        
        try:
            with mindscape_service_context() as svc:
                updated_edge = svc.update_edge(edge_id, data)
                
            style = None
            if updated_edge.appearance:
                import json
                try: style = json.loads(updated_edge.appearance)
                except: pass
                
            self.view.update_edge_visual(edge_id, style_dict=style)
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def _setup_interactions(self):
        """Enable context menus."""
        self.view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, pos):
        """Show menu for creating/linking nodes."""
        # Check if we clicked an item
        item = self.view.item_at(pos)
        
        # Edge Context Menu
        if isinstance(item, MindscapeEdgeItem):
            menu = QMenu(self)
            edge_header = menu.addAction(f"Connection #{item.edge_id}")
            if edge_header:
                edge_header.setEnabled(False)
            menu.addSeparator()
            inspect_action = menu.addAction("Inspect Connection")
            
            action = menu.exec(self.view.mapToGlobal(pos))
            if action == inspect_action:
                self._open_edge_inspector(item.edge_id)
            return

        # Background Context Menu
        if not self.view.current_focus_id and not item:
            menu = QMenu(self)
            
            # Create Root
            create_root = menu.addAction("Create First Thought")
            
            menu.addSeparator()
            
            # Import Documents
            import_docs = menu.addAction("Import Documents...")
            
            # Create Search Node
            create_search = menu.addAction("Create Search Node")
            
            action = menu.exec(self.view.mapToGlobal(pos))
            
            if action == create_root:
                self._create_root_node()
            elif action == import_docs:
                self._import_documents()
            elif action == create_search:
                self._create_search_node()
            return

        # Normal Context Menu (Linked creation)
        target_id: Optional[int] = self.view.current_focus_id
        target_name = "Focus"
        
        if isinstance(item, MindscapeNodeItem):
            target_id = item.node_id
            target_name = item.title_text
            
        # Check node type for Context Actions
        is_search_node = False
        if target_id:
             try:
                 with mindscape_service_context() as svc:
                     node_dto, _, _, _, _ = svc.get_local_graph(target_id)
                     if node_dto and node_dto.type == "search_query":
                         is_search_node = True
             except: pass
            
        menu = QMenu(self)
        
        # Header
        header_action = menu.addAction(f"Actions for: {target_name}")
        if header_action:
            header_action.setEnabled(False)
        menu.addSeparator()
        
        # Search Specific
        show_search = None
        if is_search_node:
            show_search = menu.addAction("Show Search Results")
            menu.addSeparator()
        
        # Actions
        # inspect_action = menu.addAction("Inspect Properties") # Removed duplicate
        # menu.addSeparator()
        
        add_child = menu.addAction("Add Child (Detail)")
        add_parent = menu.addAction("Add Parent (Context)")
        add_jump = menu.addAction("Jump to New...")
        
        # Document Actions
        open_doc = None
        if isinstance(item, MindscapeNodeItem):
             if item.node_type == "document":
                 menu.addSeparator()
                 open_doc = menu.addAction("Open Document")


        # Import Documents (Node Level)
        menu.addSeparator()
        import_docs_node = menu.addAction("Import Documents...")
        create_search_node = menu.addAction("Create Search Node")
        menu.addSeparator()
        inspect_action = menu.addAction("Inspect Properties")
        delete_action = menu.addAction("Delete Node")
        
        action = menu.exec(self.view.mapToGlobal(pos))
        
        if action == show_search and target_id is not None:
            self._on_node_selected(int(target_id))
        elif action == add_child:
            self._add_node(target_id, "child")
        elif action == add_parent:
            self._add_node(target_id, "parent")
        elif action == add_jump:
            self._add_node(target_id, "jump")
        elif action == inspect_action:
            if isinstance(item, MindscapeNodeItem):
                self._open_inspector(item.node_id)
            elif target_id is not None:
                self._open_inspector(target_id)
        elif action == delete_action:
            self._delete_node(target_id)
        elif open_doc and action == open_doc:
            self._open_document_node(target_id)
        elif action == import_docs_node:
            self._import_documents(target_id)
        elif action == create_search_node:
            self._create_search_node()
        elif action and action.text() == "Save Mindscape":
            self._export_mindscape()
        elif action and action.text() == "Load Mindscape":
            self._import_mindscape()

    def _create_root_node(self):
        """Create the first node in an empty graph."""
        text, ok = QInputDialog.getText(self, "New Thought", "What is on your mind?")
        if ok and text:
            try:
                with mindscape_service_context() as svc:
                    # Create without links
                    new_node = svc.create_node(text, type="concept") # Default to concept, let user organize
                
                self.view.load_graph(new_node.id)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _add_node(self, target_id, relation_role):
        """Helper to bridge context menu to _add_linked_node."""
        if relation_role == "child":
            self._add_linked_node(target_id, "parent", is_child=True)
        elif relation_role == "parent":
            self._add_linked_node(target_id, "parent", is_child=False)
        elif relation_role == "jump":
            self._add_linked_node(target_id, "jump")

    def _add_linked_node(self, source_id, relation_type, is_child=True):
        """
        Creates a new node and links it to source_id.
        if is_child=True: source -> new (source is parent)
        if is_child=False: new -> source (new is parent)
        """
        text, ok = QInputDialog.getText(self, "New Thought", "Title:")
        if ok and text:
            try:
                with mindscape_service_context() as svc:
                    new_node = svc.create_node(text)
                    
                    if relation_type == "jump":
                        svc.link_nodes(source_id, new_node.id, "jump")
                    elif is_child:
                        svc.link_nodes(source_id, new_node.id, "parent")
                    else:
                        svc.link_nodes(new_node.id, source_id, "parent")
                
                # Refresh view centered on the SOURCE (to show the new link)
                # Or maybe centering on the NEW node is better? "The Brain" centers on new.
                self.view.load_graph(new_node.id)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _delete_node(self, node_id):
        """Removes the node and refocuses."""
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            "Are you sure you want to delete this thought and its connections?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                with mindscape_service_context() as svc:
                    fallback = svc.delete_node(node_id)
                
                if fallback:
                    self.view.load_graph(fallback.id)
                else:
                    # Clear view (Blank Canvas)
                    scene_obj = self.view.scene()
                    if scene_obj:
                        scene_obj.clear()
                    self.view._items.clear()
                    self.view._edges.clear()
                    self.view.current_focus_id = None
                    self.view.update()
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _init_graph(self):
        """Bootstrap the view."""
        try:
            with mindscape_service_context() as svc:
                # Try to get the last known root or any node
                home = svc.get_home_node()
                
            if home:
                self.view.load_graph(home.id)
            # Else: stay blank, waiting for user "Create Root" action
            
        except Exception as e:
            print(f"Error initializing Mindscape: {e}")


    def _export_mindscape(self):
        """Persist the entire graph to a JSON snapshot."""
        path, _ = QFileDialog.getSaveFileName(self, "Save Mindscape", os.path.expanduser("~"), "Mindscape (*.json)")
        if not path:
            return
        try:
            with mindscape_service_context() as svc:
                snapshot = svc.export_snapshot()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "Saved", f"Mindscape exported to {path}")
        except Exception as exc:
            QMessageBox.critical(self, "Save Failed", str(exc))

    def _import_mindscape(self):
        """Load a snapshot, replacing the current graph."""
        path, _ = QFileDialog.getOpenFileName(self, "Load Mindscape", os.path.expanduser("~"), "Mindscape (*.json)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                snapshot = json.load(f)
            with mindscape_service_context() as svc:
                svc.import_snapshot(snapshot, reset=True)
                home = svc.get_home_node()
            if home:
                self.view.load_graph(home.id)
            else:
                scene_obj = self.view.scene()
                if scene_obj:
                    scene_obj.clear()
                self.view._items.clear()
                self.view._edges.clear()
                self.view.current_focus_id = None
                self.view.update()
            QMessageBox.information(self, "Loaded", f"Mindscape imported from {path}")
        except Exception as exc:
            QMessageBox.critical(self, "Load Failed", str(exc))


    def _import_documents(self, parent_id=None):
        """Batch import documents and create nodes."""
        # Consolidate parent resolution
        if not parent_id:
             parent_id = self.view.current_focus_id

        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Import Documents", 
            "", 
            "Documents (*.txt *.md *.html *.pdf);;All Files (*)"
        )
        
        if not files:
            return
            
        class ImportSignals(QObject):
            finished = pyqtSignal(int, object, list)  # imported_count, last_node_id, errors

        class ImportTask(QRunnable):
            def __init__(self, parent_id, files, signals):
                super().__init__()
                self.parent_id = parent_id
                self.files = files
                self.signals = signals

            def run(self):
                imported = 0
                last_node_id = None
                errors = []
                with document_service_context() as doc_service:
                    with mindscape_service_context() as mind_service:
                        for f in self.files:
                            try:
                                doc = doc_service.import_document(f)
                                doc_id = int(getattr(doc, "id", 0))
                                doc_title = str(getattr(doc, "title", ""))
                                metadata = {"document_id": doc_id}
                                mind_node = mind_service.create_node(
                                    title=doc_title,
                                    type="document",
                                    content=f"Linked Document: {doc_title}",
                                    metadata_payload=metadata,
                                    document_id=doc_id,
                                    appearance={"shape": "document", "color_override": "#e0f2fe", "textColor": "#0f172a", "borderColor": "#0284c7", "borderWidth": 1}
                                )
                                if self.parent_id:
                                    mind_service.link_nodes(self.parent_id, mind_node.id, "jump")
                                imported += 1
                                last_node_id = mind_node.id
                            except Exception as e:
                                errors.append((f, str(e)))
                self.signals.finished.emit(imported, last_node_id, errors)

        sig = ImportSignals()

        def _on_finished(imported_count, last_node_id, errors):
            if imported_count > 0:
                if self.view.current_focus_id:
                    self.view.load_graph(self.view.current_focus_id)
                elif last_node_id:
                    self.view.load_graph(last_node_id)
                QMessageBox.information(self, "Import Complete", f"Imported {imported_count} documents.")
            if errors:
                msg = "\n".join([f"{f}: {err}" for f, err in errors])
                QMessageBox.warning(self, "Import Errors", msg)

        sig.finished.connect(_on_finished)
        self.thread_pool.start(ImportTask(parent_id, files, sig))

    def _open_document_node(self, node_id):
        """Open the linked document in editor."""
        print(f"[Window] Attempting to open document for node {node_id}")
        # 1. Get Node to find document_id
        doc_id = None
        with mindscape_service_context() as service:
            focus_dto, _, _, _, _ = service.get_local_graph(node_id)
            if focus_dto:
                print(f"[Window] Found node {node_id}, metadata: {focus_dto.metadata_payload}")
                if focus_dto.metadata_payload:
                    try:
                        meta = json.loads(focus_dto.metadata_payload)
                        doc_id = meta.get("document_id")
                        print(f"[Window] Extracted document_id: {doc_id}")
                    except Exception as e:
                        print(f"[Window] Failed to parse metadata: {e}")
                        pass
        
        if not doc_id:
            QMessageBox.warning(self, "Error", "Node is not linked to a valid document.")
            return

        # 2. Get Document and Open Editor
        with document_service_context() as doc_service:
            doc = doc_service.get_document(doc_id)
            if not doc:
                QMessageBox.warning(self, "Error", "Linked document not found in library.")
                return
            
            print(f"[Window] Opening editor for document: {doc.title}")
            # Launch Editor
            self.doc_editor = DocumentEditorWindow(self) 
            self.doc_editor.load_document_model(doc)
            self.doc_editor.show()


