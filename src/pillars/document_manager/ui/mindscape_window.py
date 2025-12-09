
from PyQt6.QtWidgets import (
    QMainWindow, QGraphicsView, QDockWidget, QMenu, QMessageBox, 
    QInputDialog, QFileDialog, QWidget, QVBoxLayout
)
from PyQt6.QtCore import Qt, QTimer
from .mindscape_view import MindscapeView
from .mindscape_inspector import NodeInspectorWidget
from ..services.mindscape_service import mindscape_service_context
from ..services.document_service import document_service_context
from .document_editor_window import DocumentEditorWindow
import json

class MindscapeWindow(QMainWindow):
    """
    Mindscape 3.0: The Living Graph
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mindscape: The Living Graph")
        self.resize(1400, 800) # Slightly wider for dock
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.view = MindscapeView()
        self.layout.addWidget(self.view)
        
        # Inspector Dock
        self.inspector = NodeInspectorWidget()
        self.dock = QDockWidget("Inspector", self)
        self.dock.setWidget(self.inspector)
        self.dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)
        self.dock.hide() # Hidden by default
        
        # Signals
        # self.view.node_selected.connect(self._on_node_selected) # Disconnected per user request
        # self.view.edge_selected.connect(self._on_edge_selected) # Disconnected per user request (Context only)
        self.inspector.node_updated.connect(self._save_node_changes)
        self.inspector.edge_updated.connect(self._save_edge_changes)
        
        self._init_graph()
        self._setup_interactions()

    def _open_inspector(self, node_id):
        """Manually open inspector for a specific node."""
        self.dock.show()
        self._on_node_selected(node_id)

    def _open_edge_inspector(self, edge_id):
        """Manually open inspector for a specific edge."""
        self.dock.show()
        self._on_edge_selected(edge_id)

    def _on_node_selected(self, node_id):
        """Fetch full details for the inspector."""
        try:
            with mindscape_service_context() as svc:
                focus, _, _, _ = svc.get_local_graph(node_id)
                self.inspector.set_data(focus, "node")
        except Exception as e:
            print(f"Error fetching node details: {e}")

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
        if hasattr(item, "edge_id"):
            menu = QMenu(self)
            menu.addAction(f"Connection #{item.edge_id}").setEnabled(False)
            menu.addSeparator()
            inspect_action = menu.addAction("Inspect Connection")
            
            action = menu.exec(self.view.mapToGlobal(pos))
            if action == inspect_action:
                self._open_edge_inspector(item.edge_id)
            return

        # If no focus (Empty Graph) and no item clicked, allow creating Root
            if action == create_root:
                self._create_root_node()
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
        target_id = self.view.current_focus_id
        target_name = "Focus"
        
        if hasattr(item, "node_id"):
            target_id = item.node_id
            target_name = item.title_text
            
        menu = QMenu(self)
        
        # Header
        menu.addAction(f"Actions for: {target_name}").setEnabled(False)
        menu.addSeparator()
        
        # Actions
        # inspect_action = menu.addAction("Inspect Properties") # Removed duplicate
        # menu.addSeparator()
        
        add_child = menu.addAction("Add Child (Detail)")
        add_parent = menu.addAction("Add Parent (Context)")
        add_jump = menu.addAction("Jump to New...")
        
        # Document Actions
        open_doc = None
        if hasattr(item, "node_id"):
             # Check if it's a document node
             # We need to peek at the node data or use the item properties if we stored type on item
             # The item doesn't currently store DTO, but we can check if it has 'document' type logic
             # For now, let's just checking item.node_type if we added that, or fetch.
             # Easier: Always check service or rely on item having type. 
             # Item has `node_type`!
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
        
        if action == add_child:
            self._add_node(target_id, "child")
        elif action == add_parent:
            self._add_node(target_id, "parent")
        elif action == add_jump:
            self._add_node(target_id, "jump")
        elif action == inspect_action:
            if hasattr(item, "node_id"):
                 self._open_inspector(item.node_id)
            else:
                 # If clicked focus via background menu or similar logic
                 self._open_inspector(target_id)
        elif action == delete_action:
            self._delete_node(target_id)
        elif open_doc and action == open_doc:
            self._open_document_node(target_id)
        elif action == import_docs_node:
            self._import_documents(target_id)
        elif action == create_search_node:
            self._create_search_node()

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
                    self.view.scene.clear()
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
        except Exception as e:
            print(f"Error initializing Mindscape: {e}")

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
            
        imported_count = 0
        
        with document_service_context() as doc_service:
            with mindscape_service_context() as mind_service:
                for f in files:
                    try:
                        # 1. Import to Document Pillar
                        doc = doc_service.import_document(f)
                        
                        # 2. Create MindNode
                        metadata = {"document_id": doc.id}
                        
                        # Use file name as title
                        mind_node = mind_service.create_node(
                            title=doc.title,
                            type="document",
                            content=f"Linked Document: {doc.title}",
                            metadata_payload=metadata,
                            appearance={"shape": "document", "color_override": "#e0f2fe", "textColor": "#0f172a", "borderColor": "#0284c7", "borderWidth": 1} 
                        )
                        
                        # 3. Link if valid parent
                        if parent_id:
                            # If we are focused on a node, link these as Jumps (Associations) or Children?
                            # Let's link as Jumps for now as Documents are usually reference material.
                            mind_service.link_nodes(parent_id, mind_node.id, "jump")
                            
                        imported_count += 1
                    except Exception as e:
                        print(f"Failed to import {f}: {e}")
                        
        if imported_count > 0:
            # Reload graph
            if self.view.current_focus_id:
                self.view.load_graph(self.view.current_focus_id)
            elif mind_node:
                self.view.load_graph(mind_node.id)
                
            QMessageBox.information(self, "Import Complete", f"Imported {imported_count} documents.")

    def _open_document_node(self, node_id):
        """Open the linked document in editor."""
        print(f"[Window] Attempting to open document for node {node_id}")
        # 1. Get Node to find document_id
        doc_id = None
        with mindscape_service_context() as service:
            focus_dto, _, _, _ = service.get_local_graph(node_id)
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

    def _create_search_node(self):
        """Create a node based on search results."""
        term, ok = QInputDialog.getText(self, "Create Search Node", "Enter search term:")
        if not ok or not term.strip():
            return
            
        with document_service_context() as doc_service:
            # Search
            results = doc_service.search_documents_with_highlights(term, limit=20)
            
            if not results:
                QMessageBox.information(self, "No Results", f"No documents found for '{term}'")
                return
                
            with mindscape_service_context() as mind_service:
                # 1. Create Central Search Node
                # Hexagon shape, distinctive color
                search_node = mind_service.create_node(
                    title=f"Search: {term}",
                    type="search_query",
                    content=f"Search Query for: '{term}'\nResults: {len(results)}",
                    appearance={"shape": "hexagon", "color_override": "#8b5cf6", "textColor": "#ffffff", "borderWidth": 2}
                )
                
                # 2. Create Child Nodes for Results
                for res in results:
                    # Parse snippet
                    snippet = res.get('highlights', 'No preview available.')
                    # Convert HTML snippet to text if needed, or keep as is? 
                    # MindscapeNode currently displays raw text usually, but RichTextEditor can handle HTML.
                    # For Node Content popup (if we had one), HTML is good.
                    # For now, let's store it as content.
                    
                    doc_id = res['id']
                    
                    # Create Node
                    res_node = mind_service.create_node(
                        title=res['title'],
                        type="document",
                        content=snippet,
                        metadata_payload={"document_id": doc_id},
                        appearance={"shape": "document", "color_override": "#e0f2fe", "textColor": "#0f172a", "borderColor": "#0284c7"}
                    )
                    
                    # Link to Search Node
                    mind_service.link_nodes(search_node.id, res_node.id, "parent") # Search Node is Parent
                    
                # 3. Load Graph centered on Search Node
                self.view.load_graph(search_node.id)
                QMessageBox.information(self, "Search Complete", f"Created search node with {len(results)} results.")
