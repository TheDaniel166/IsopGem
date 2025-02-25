"""
Chat panel for interacting with Karnak
"""
import logging
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QLineEdit, QLabel
)
from PyQt6.QtCore import Qt
from qasync import asyncSlot

from ..base import BasePanel
from ....ai.karnak_chat import KarnakChat
from ....ai.rag_manager import RAGManager

logger = logging.getLogger(__name__)

class ChatPanel(BasePanel):
    """Panel for chatting with Karnak"""
    
    def __init__(self, parent=None):
        super().__init__(parent, title="Karnak - Spiritual Guide")
        self.rag = RAGManager()
        self.karnak = KarnakChat(self.rag)
        
    def setup_ui(self):
        """Set up the chat panel UI"""
        # Chat history
        self.chat_history = QTextEdit(self)
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Ask Karnak for guidance...")
        self.input_field.returnPressed.connect(self._on_send_clicked)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        self.send_btn = QPushButton("Ask", self)
        self.send_btn.clicked.connect(self._on_send_clicked)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)
        
        # Main layout
        self.content_layout.addWidget(self.chat_history)
        self.content_layout.addLayout(input_layout)
        
        # Welcome message
        self.chat_history.append(
            "Welcome, seeker of wisdom. I am Karnak, named after the ancient temple "
            "of spiritual knowledge. How may I guide you today?"
        )
        
    @asyncSlot()
    async def _on_send_clicked(self):
        """Handle send button click"""
        try:
            query = self.input_field.text().strip()
            if not query:
                return
                
            # Clear input
            self.input_field.clear()
            
            # Show user message
            self.chat_history.append(f"\nYou: {query}")
            
            # Get Karnak's response
            self.send_btn.setEnabled(False)
            response = await self.karnak.get_response(query)
            self.chat_history.append(f"\nKarnak: {response}\n")
            
            # Scroll to bottom
            self.chat_history.verticalScrollBar().setValue(
                self.chat_history.verticalScrollBar().maximum()
            )
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            self.chat_history.append(
                "\nKarnak: I apologize, but I am unable to access the wisdom "
                "at this moment. Please try again."
            )
        finally:
            self.send_btn.setEnabled(True)
            
    def get_preferred_area(self):
        """Get the preferred docking area"""
        return Qt.DockWidgetArea.RightDockWidgetArea
