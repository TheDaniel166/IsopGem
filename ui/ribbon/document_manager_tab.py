from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, 
                            QPushButton, QLineEdit, QStackedWidget, QLabel,
                            QTreeView, QCalendarWidget, QListWidget)
from PyQt5.QtCore import Qt
from ui.workspace.document_manager.categories.actions import DocumentActions 

class DocumentManagerTab(QWidget):
    def __init__(self, panel_manager):
        super().__init__()
        self.panel_manager = panel_manager
        self.document_actions = DocumentActions(self)
        self.setup_ui()

    def setup_ui(self):
        # First create and store panel references
        self.navigation_panel = self.create_navigation_panel()
        self.content_panel = self.create_content_panel()
        self.details_panel = self.create_details_panel()

        # Create and set layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.navigation_panel)
        main_layout.addWidget(self.content_panel)
        main_layout.addWidget(self.details_panel)
        self.setLayout(main_layout)

        # Connect actions after panels are created
        create_new_btn = self.details_panel.findChild(QPushButton, "Create New")
        import_btn = self.details_panel.findChild(QPushButton, "Import")  # Changed from actions_group to details_panel
        
        create_new_btn.clicked.connect(self.document_actions.create_new_document)
        import_btn.clicked.connect(self.document_actions.show_import_dialog)
        
    def create_navigation_panel(self):
        nav_panel = QWidget()
        nav_layout = QVBoxLayout()
        
        # Documents Group
        docs_group = QGroupBox("Documents")
        docs_layout = QVBoxLayout()
        
        # Configure document buttons
        all_docs_btn = QPushButton("All Documents")
        all_docs_btn.setObjectName("AllDocuments")
        
        categories_btn = QPushButton("Categories")
        categories_btn.setObjectName("Categories")
        categories_btn.clicked.connect(
            lambda: self.panel_manager.create_panel('categories')
        )
        
        favorites_btn = QPushButton("Favorites")
        favorites_btn.setObjectName("Favorites")
        
        docs_layout.addWidget(all_docs_btn)
        docs_layout.addWidget(categories_btn)
        docs_layout.addWidget(favorites_btn)
        docs_group.setLayout(docs_layout)
        
        # Notes Group - Streamlined
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout()
        
        all_notes_btn = QPushButton("All Notes")
        all_notes_btn.setObjectName("AllNotes")
        
        note_categories_btn = QPushButton("Categories")
        note_categories_btn.setObjectName("NoteCategories")
        
        notes_layout.addWidget(all_notes_btn)
        notes_layout.addWidget(note_categories_btn)
        notes_group.setLayout(notes_layout)
        
        # Tasks Group
        tasks_group = QGroupBox("Tasks")
        tasks_layout = QVBoxLayout()
        
        todo_btn = QPushButton("To-Do List")
        todo_btn.setObjectName("TodoList")
        
        calendar_btn = QPushButton("Calendar View")
        calendar_btn.setObjectName("CalendarView")
        
        tasks_layout.addWidget(todo_btn)
        tasks_layout.addWidget(calendar_btn)
        tasks_group.setLayout(tasks_layout)
        
        # Add groups to navigation panel
        nav_layout.addWidget(docs_group)
        nav_layout.addWidget(notes_group)
        nav_layout.addWidget(tasks_group)
        nav_layout.addStretch()
        
        nav_panel.setLayout(nav_layout)
        nav_panel.setFixedWidth(200)
        return nav_panel 
    
    def create_content_panel(self):
        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(self.create_dashboard_page())
        self.content_stack.addWidget(self.create_documents_page())
        self.content_stack.addWidget(self.create_notes_page())
        self.content_stack.addWidget(self.create_tasks_page())
        return self.content_stack

    def create_details_panel(self):
        details_panel = QWidget()
        details_layout = QVBoxLayout()
        
        # Actions Group
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout()
        
        # Create buttons with object names
        create_new_btn = QPushButton("Create New")
        create_new_btn.setObjectName("Create New")
        
        import_btn = QPushButton("Import")
        import_btn.setObjectName("Import")
        
        # Common actions
        actions_layout.addWidget(create_new_btn)
        actions_layout.addWidget(QPushButton("Edit"))
        actions_layout.addWidget(QPushButton("Delete"))
        actions_layout.addWidget(import_btn)        
        actions_layout.addWidget(QPushButton("Export"))
        
        # Organization actions
        actions_layout.addWidget(QPushButton("Filter"))
        actions_layout.addWidget(QPushButton("Sort"))
        actions_layout.addWidget(QPushButton("Tag"))
        
        actions_group.setLayout(actions_layout)
        
        # Search Group
        search_group = QGroupBox("Search")
        search_layout = QVBoxLayout()
        search_layout.addWidget(QLineEdit())
        search_layout.addWidget(QPushButton("Advanced Search"))
        search_layout.addWidget(QPushButton("Save Search"))
        search_group.setLayout(search_layout)
        
        details_layout.addWidget(actions_group)
        details_layout.addWidget(search_group)
        details_layout.addStretch()
        
        details_panel.setLayout(details_layout)
        details_panel.setFixedWidth(200)
        return details_panel
        
    def create_dashboard_page(self):
        page = QWidget()
        layout = QGridLayout()
        
        # Column 1
        dashboard_view = QListWidget()
        documents_view = QListWidget()
        layout.addWidget(QLabel("Dashboard"), 0, 0)
        layout.addWidget(dashboard_view, 1, 0)
        layout.addWidget(QLabel("Documents"), 2, 0)
        layout.addWidget(documents_view, 3, 0)
        
        # Column 2
        notes_view = QListWidget()
        tasks_view = QListWidget()
        layout.addWidget(QLabel("Notes"), 0, 1)
        layout.addWidget(notes_view, 1, 1)
        layout.addWidget(QLabel("Tasks"), 2, 1)
        layout.addWidget(tasks_view, 3, 1)
        
        # Column 3
        actions_view = QListWidget()
        search_view = QListWidget()
        layout.addWidget(QLabel("Actions"), 0, 2)
        layout.addWidget(actions_view, 1, 2)
        layout.addWidget(QLabel("Search"), 2, 2)
        layout.addWidget(search_view, 3, 2)
        
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        
        page.setLayout(layout)
        return page
        
    def create_documents_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        tree = QTreeView()
        layout.addWidget(tree)
        page.setLayout(layout)
        return page
        
    def create_notes_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        notes_list = QListWidget()
        layout.addWidget(notes_list)
        page.setLayout(layout)
        return page
        
    def create_tasks_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        calendar = QCalendarWidget()
        layout.addWidget(calendar)
        task_list = QListWidget()
        layout.addWidget(task_list)
        page.setLayout(layout)
        return page
