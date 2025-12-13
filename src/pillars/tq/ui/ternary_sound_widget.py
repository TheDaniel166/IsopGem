from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTextEdit, QFrame, 
                             QTabWidget, QPlainTextEdit, QListWidget, QSplitter,
                             QCheckBox)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from ..models.amun_sound import AmunSoundCalculator
from ..services.amun_audio_service import AmunAudioService
from ..services.kamea_symphony_service import KameaSymphonyService
from ..services.kamea_grid_service import KameaGridService
from .amun_visualizer import AmunVisualizer

class CalculatorTab(QWidget):
    """Tab for calculating single Ditrunes."""
    def __init__(self, output_display: QTextEdit, main_window):
        super().__init__()
        self.main_window = main_window
        self.output_display = output_display
        self.calculator = AmunSoundCalculator()
        self.kamea_service = KameaSymphonyService()
        self.current_result = None
        
        # Audio
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Input Frame
        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(0,0,0,0)
        
        self.le_input = QLineEdit()
        self.le_input.setPlaceholderText("Ditrune (0-728)")
        self.le_input.returnPressed.connect(self.calculate)
        
        btn_calc = QPushButton("Calculate")
        btn_calc.clicked.connect(self.calculate)
        
        self.btn_play = QPushButton("Play")
        self.btn_play.setEnabled(False)
        self.btn_play.clicked.connect(self.play_sound)
        
        input_layout.addWidget(QLabel("Ditrune:"))
        input_layout.addWidget(self.le_input)
        input_layout.addWidget(btn_calc)
        input_layout.addWidget(btn_calc)
        input_layout.addWidget(self.btn_play)
        
        self.chk_grand = QCheckBox("Grand Edition")
        self.chk_grand.setToolTip("Use Kinetic Audio Engine (NumPy High-Res)")
        input_layout.addWidget(self.chk_grand)
        
        layout.addWidget(input_frame)
        layout.addStretch()

    def calculate(self):
        input_text = self.le_input.text().strip()
        try:
            val = int(input_text)
            if not (0 <= val <= 728): raise ValueError("Range 0-728")
            
            self.current_result = self.calculator.calculate_signature(val)
            self._display_results(self.current_result)
            self.btn_play.setEnabled(True)
            
            # Notify parent to update visualizer
            if self.main_window:
                self.main_window.update_visualizer(self.current_result)
            
        except ValueError as e:
            self.output_display.setHtml(f"<span style='color:red'>{e}</span>")
            self.btn_play.setEnabled(False)

    def _display_results(self, data: dict):
        meta = data['meta']
        ch = data['channels']
        
        ch1, ch2, ch3 = ch[1], ch[2], ch[3]
        
        # Extract Family info
        params = data.get('parameters', {})
        family_name = params.get('family_name', 'UNKNOWN')
        family_col = params.get('color_hex', '#ffffff')
        
        html = f"""
        <h2 style='color:{family_col}'>{family_name.upper()} Family</h2>
        <h3>Ditrune {meta['decimal']}</h3>
        <p><b>Configuration:</b> {meta['ternary']}</p>
        <hr>
        <table border='0' cellpadding='5'>
        <tr>
            <td><b>Red (Body)</b></td>
            <td>{ch1['desc']}</td>
            <td>{ch1['output']}</td>
        </tr>
        <tr>
            <td><b>Green (Breath)</b></td>
            <td>{ch2['desc']}</td>
            <td>{ch2['output']}</td>
        </tr>
        <tr>
            <td><b>Blue (Soul)</b></td>
            <td>{ch3['desc']}</td>
            <td>{ch3['output']}</td>
        </tr>
        </table>
        """
        self.output_display.setHtml(html)

    def play_sound(self):
        if not self.current_result: return
        
        # Update Visualizer immediately before play
        if self.main_window:
            self.main_window.update_visualizer(self.current_result)

        # Updated for RGB structure
        # Ch1 = Red (Pitch), Ch2 = Green (Dyn), Ch3 = Blue (Timbre)
        # Note: AmunSoundCalculator output structure:
        # 1: Pitch (Red) -> value, output (freq string)
        # 2: Dynamics (Green) -> value, output (amp string)
        # 3: Timbre (Blue) -> value, output (waveform)
        
        # But wait! I need the raw floats for generation, not just strings.
        # AmunSoundCalculator returns 'parameters' dict too.
        params = self.current_result['parameters']
        # Grand Edition Check
        if self.chk_grand.isChecked():
            # Use KameaSymphonyService
            try:
                nucleation = self.current_result.get('nucleation')
                if not nucleation:
                     print("Error: Nucleation data missing.")
                     return
                
                path = self.kamea_service.generate_wav_file(nucleation)
                self.player.setSource(QUrl.fromLocalFile(path))
                self.audio_output.setVolume(85) # Grand might be cleaner?
                self.player.play()
                return
            except Exception as e:
                print(f"Grand Play Error: {e}")
                return

        # Standard Engine (AmunAudioService)
        freq = params['freq']
        attack = params['attack']
        release = params['release']
        layers = params['layers']
        detune = params['detune']
        audio_type = params.get('audio_type', 'Standard')
        
        try:
            path = AmunAudioService.generate_wave_file(freq, attack, release, layers, detune, audio_type)
            self.player.setSource(QUrl.fromLocalFile(path))
            self.audio_output.setVolume(75)
            self.player.play()
        except Exception as e:
            print(f"Play Error: {e}")

class ComposerTab(QWidget):
    """Tab for composing sequences."""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.calculator = AmunSoundCalculator()
        self.kamea_service = KameaSymphonyService() # Instance
        self.grid_service = KameaGridService()      # Instance for Chords
        self.sequence_data = [] # List of signature dicts
        
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Input Area
        self.txt_input = QPlainTextEdit()
        self.txt_input.setPlaceholderText("Enter Ditrunes separated by commas or spaces...\nExample: 91, 182, 364")
        self.txt_input.setMaximumHeight(80)
        
        # Controls
        ctrl_layout = QHBoxLayout()
        btn_parse = QPushButton("Parse Sequence")
        btn_parse.clicked.connect(self.parse_sequence)
        
        self.btn_play_seq = QPushButton("Play Sequence")
        self.btn_play_seq.setEnabled(False)
        self.btn_play_seq.clicked.connect(self.play_sequence)
        
        self.btn_chord = QPushButton("Play Chord")
        self.btn_chord.setEnabled(False)
        self.btn_chord.clicked.connect(self.play_chord)
        
        self.chk_grand_seq = QCheckBox("Grand Mode")
        self.chk_grand_seq.setToolTip("Use Kamea Symphony Engine")
        
        btn_map_chord = QPushButton("Map Chord")
        btn_map_chord.setToolTip("Find Geometric Sybilings (Quadset)")
        btn_map_chord.clicked.connect(self.map_chord)
        
        ctrl_layout.addWidget(btn_parse)
        ctrl_layout.addWidget(btn_map_chord)
        ctrl_layout.addWidget(self.btn_play_seq)
        ctrl_layout.addWidget(self.btn_chord)
        ctrl_layout.addWidget(self.chk_grand_seq)
        
        # List View
        self.list_widget = QListWidget()
        
        layout.addWidget(QLabel("Composer Input:"))
        layout.addWidget(self.txt_input)
        layout.addLayout(ctrl_layout)
        layout.addWidget(self.list_widget)
        
    def parse_sequence(self):
        text = self.txt_input.toPlainText()
        # Replace commas with spaces and split
        tokens = text.replace(',', ' ').split()
        
        self.sequence_data = []
        self.list_widget.clear()
        
        for token in tokens:
            try:
                val = int(token)
                if 0 <= val <= 728:
                    sig = self.calculator.calculate_signature(val)
                    self.sequence_data.append(sig)
                    
                    # Add to list
                    param = sig['parameters']
                    item_text = f"Ditrune {val}: {param['freq']:.1f}Hz, {param['layers']} Layers, {param['attack']}s Atk"
                    self.list_widget.addItem(item_text)
            except ValueError:
                continue
                
        if self.sequence_data:
            self.btn_play_seq.setEnabled(True)
            self.btn_chord.setEnabled(True)
            
    def play_sequence(self):
        if not self.sequence_data: return
        
        try:
            # Activate visualizer with first note to show activity
            if self.main_window and self.sequence_data:
                self.main_window.update_visualizer(self.sequence_data[0])

            # Generate full sequence file
            path = ""
            
            if self.chk_grand_seq.isChecked():
                # Extract nucleations
                nucleations = [s.get('nucleation') for s in self.sequence_data if s.get('nucleation')]
                if not nucleations:
                    print("No nucleation data for Grand Mode")
                    return
                path = self.kamea_service.generate_sequence(nucleations, duration=0.5)
            else:
                # Standard Engine
                path = AmunAudioService.generate_sequence(self.sequence_data, note_duration=0.5)
                
            self.player.setSource(QUrl.fromLocalFile(path))
            self.audio_output.setVolume(80)
            self.player.play()
            
            # TODO: Animate visualizer through sequence? 
            # That requires synchronization. For now, Visualizer shows last item or static.
        except Exception as e:
            print(f"Seq Play Error: {e}")

    def play_chord(self):
        """Play all notes simultaneously."""
        if not self.sequence_data: return
        
        try:
            # Force Grand Mode for Chords (easier implementation via NumPy)
            # Or implement chord logic in AmunAudioService.
            # Currently only Kamea has explicit chord mix.
            
            # Extract nucleations
            nucleations = [s.get('nucleation') for s in self.sequence_data if s.get('nucleation')]
            
            if nucleations:
                 # Use Kamea Service
                 path = self.kamea_service.generate_chord(nucleations, duration=4.0)
                 self.player.setSource(QUrl.fromLocalFile(path))
                 self.audio_output.setVolume(80)
                 self.player.play()
            else:
                 print("Chord requires valid data (Nucleation missing?).")

        except Exception as e:
            print(f"Chord Play Error: {e}")

    def map_chord(self):
        """
        Takes the first valid number in the input, finds its Quadset,
        and replaces the input text with the chord members.
        """
        text = self.txt_input.toPlainText()
        tokens = text.replace(',', ' ').split()
        
        seed = None
        for t in tokens:
            try:
                val = int(t)
                if 0 <= val <= 728:
                    seed = val
                    break
            except: continue
            
        if seed is not None:
            # Get Chord Values
            try:
                chord = self.grid_service.get_chord_values(seed)
                # Format as string
                chord_str = ", ".join(str(x) for x in chord)
                self.txt_input.setPlainText(chord_str)
                # Auto-parse to update list
                self.parse_sequence()
            except Exception as e:
                print(f"Map Chord Error: {e}")
        else:
             self.txt_input.setPlaceholderText("Enter a seed number first (e.g. 10)")

class TernarySoundWidget(QWidget):
    """Main Widget hosting Calculator and Composer tabs + Visualizer."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Amun Sound System")
        self.resize(800, 600) # Wider for visualizer
        
        layout = QHBoxLayout(self)
        
        # Left Panel: Control Tabs
        left_panel = QTabWidget()
        
        # Shared Output Display (for detailed single view)
        self.txt_output = QTextEdit()
        self.txt_output.setReadOnly(True)
        self.txt_output.setMaximumHeight(200)
        
        # Tabs
        self.calc_tab = CalculatorTab(self.txt_output, self)
        self.comp_tab = ComposerTab(self)
        
        left_panel.addTab(self.calc_tab, "Calculator")
        left_panel.addTab(self.comp_tab, "Composer")
        
        # Left Layout container
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.addWidget(left_panel)
        left_layout.addWidget(QLabel("Detailed Output:"))
        left_layout.addWidget(self.txt_output)
        
        # Right Panel: Visualizer
        self.visualizer = AmunVisualizer()
        
        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_container)
        splitter.addWidget(self.visualizer)
        splitter.setStretchFactor(1, 1) # Give visualizer more space
        
        layout.addWidget(splitter)
        
    def update_visualizer(self, result: dict):
        """Update the visualizer with new signature data."""
        params = result['parameters']
        # Pass full params to updated Visualizer
        self.visualizer.update_parameters(params)
        # Ideally update visualizer to show Rings based on Bigram! 
        # But for now we just prevent crash.
