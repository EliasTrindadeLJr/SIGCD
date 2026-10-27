import uuid
import tempfile
from pathlib import Path

import cv2

from PySide6.QtCore import QTimer, Qt, QSettings, QPoint, QPointF
from PySide6.QtGui import QImage, QPixmap, QPainter, QPen, QColor
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
    QCheckBox,
    QFrame,
    QFormLayout,
    QMessageBox,
    QInputDialog,
    QProgressBar,
    QScrollArea,
)

from handify.config.manager import ConfigManager
from handify.actions.executor import ActionExecutor
from handify.recognition.gesture_recognizer import GestureRecognizer
from handify.recognition.controller import GestureController


# =========================================================
# TEMA
# =========================================================
# Grafite azulado + índigo suave como destaque.
# Verde = sucesso, âmbar = aviso, coral = erro.

STYLE_TEMPLATE = """
* {
    font-family: "Inter", "Segoe UI", "Noto Sans", sans-serif;
    font-size: 13px;
    color: @text;
}

QMainWindow, QScrollArea, QScrollArea > QWidget > QWidget {
    background: @bg;
}

QDialog, QInputDialog, QMessageBox {
    background: @bg;
}
QDialog QLabel, QInputDialog QLabel, QMessageBox QLabel {
    background: transparent;
    color: @text;
    font-size: 13px;
}
QDialog QPushButton, QMessageBox QPushButton {
    min-width: 84px;
}
QDialog QPushButton:default, QMessageBox QPushButton:default {
    background: @accent;
    border-color: @accent;
    color: #FFFFFF;
}

QFrame#card {
    background: @card;
    border: 1px solid @border;
    border-radius: 12px;
}

QLabel#cardTitle {
    font-size: 15px;
    font-weight: 600;
    color: @title;
}

QLabel#muted {
    color: @muted;
}

QLabel#video {
    background: @video;
    border: 1px solid @border;
    border-radius: 12px;
    color: @videotext;
    font-size: 15px;
}

QLabel#gestureName {
    font-size: 22px;
    font-weight: 600;
    color: @gesture;
}

QLabel#status {
    background: @surface;
    border-radius: 8px;
    padding: 9px 12px;
    color: @statustext;
}
QLabel#status[kind="ok"]    { background: @okbg; color: @okfg; }
QLabel#status[kind="warn"]  { background: @warnbg; color: @warnfg; }
QLabel#status[kind="error"] { background: @errbg; color: @errfg; }

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background: @field;
    border: 1px solid @inputborder;
    border-radius: 8px;
    padding: 7px 10px;
    min-height: 20px;
    selection-background-color: @accent;
}
QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover {
    border-color: @hoverborder;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: @focus;
}
QComboBox::drop-down { border: none; width: 26px; }
QComboBox QAbstractItemView {
    background: @card;
    border: 1px solid @inputborder;
    selection-background-color: @selected;
    outline: none;
}

QSpinBox, QDoubleSpinBox {
    padding-right: 30px;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 26px;
    margin: 1px 1px 0 0;
    border: none;
    border-left: 1px solid @inputborder;
    border-top-right-radius: 7px;
    background: transparent;
}

QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 26px;
    margin: 0 1px 1px 0;
    border: none;
    border-left: 1px solid @inputborder;
    border-bottom-right-radius: 7px;
    background: transparent;
}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background: @surface;
}

QSpinBox::up-button:pressed, QDoubleSpinBox::up-button:pressed,
QSpinBox::down-button:pressed, QDoubleSpinBox::down-button:pressed {
    background: @btnpressed;
}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    image: url(@uparrow);
    width: 12px;
    height: 12px;
}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    image: url(@downarrow);
    width: 12px;
    height: 12px;
}

QPushButton {
    background: @btn;
    border: 1px solid @btnborder;
    border-radius: 8px;
    padding: 9px 16px;
    font-weight: 500;
}
QPushButton:hover   { background: @btnhover; }
QPushButton:pressed { background: @btnpressed; }
QPushButton:focus   { border-color: @focus; }

QPushButton#primary {
    background: @accent;
    border: 1px solid @accent;
    color: #FFFFFF;
    font-weight: 600;
}
QPushButton#primary:hover   { background: @accenthover; }
QPushButton#primary:pressed { background: @accentpressed; }

QPushButton#danger {
    background: transparent;
    border: 1px solid @dangerborder;
    color: @errfg;
}
QPushButton#danger:hover { background: @errbg; }

QListWidget {
    background: @field;
    border: 1px solid @border;
    border-radius: 10px;
    padding: 4px;
    outline: none;
}
QListWidget::item {
    padding: 9px 10px;
    border-radius: 7px;
}
QListWidget::item:hover    { background: @surface; }
QListWidget::item:selected { background: @selected; color: @selectedtext; }

QCheckBox { spacing: 8px; }
QCheckBox::indicator {
    width: 18px; height: 18px;
    border-radius: 5px;
    border: 1px solid @hoverborder;
    background: @field;
}
QCheckBox::indicator:checked {
    background: @accent;
    border-color: @accent;
}

QProgressBar {
    background: @field;
    border: none;
    border-radius: 4px;
    max-height: 8px;
    min-height: 8px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    background: @accent;
    border-radius: 4px;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: @scroll;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QFrame#divider { background: @border; }

QToolTip {
    background: @surface;
    color: @text;
    border: 1px solid @btnborder;
    padding: 4px 8px;
}
"""

PALETTES = {
    "light": {
        "bg": "#EEF0F6", "field": "#F6F7FB", "card": "#FFFFFF",
        "border": "#DDE1EC", "title": "#151A2B", "text": "#232A3D",
        "muted": "#6A7390", "video": "#E4E8F2", "videotext": "#7A829C",
        "surface": "#EDF0F8", "statustext": "#4A5270",
        "okbg": "#DDF3E5", "okfg": "#1F6B3F",
        "warnbg": "#FBEFD0", "warnfg": "#7A5A10",
        "errbg": "#FBE1E3", "errfg": "#A12B36",
        "inputborder": "#CBD1E1", "hoverborder": "#AEB6CE",
        "focus": "#6F7DFF", "accent": "#5A69F0",
        "accenthover": "#6D7BFF", "accentpressed": "#4A58DB",
        "selected": "#DDE1FF", "selectedtext": "#1D2250",
        "btn": "#EEF0F8", "btnborder": "#D3D8E6",
        "btnhover": "#E3E7F4", "btnpressed": "#D8DDEE",
        "dangerborder": "#EBC3C7", "scroll": "#C3C9DA",
        "gesture": "#4A58DB",
    },
    "dark": {
        "bg": "#171A23", "field": "#171A23", "card": "#1F2330",
        "border": "#2C3142", "title": "#F4F6FC", "text": "#E6E9F2",
        "muted": "#8B93AA", "video": "#0F1117", "videotext": "#6B7390",
        "surface": "#232838", "statustext": "#B9C0D6",
        "okbg": "#1E3329", "okfg": "#8FE0B0",
        "warnbg": "#3A3120", "warnfg": "#F0CD85",
        "errbg": "#3C2326", "errfg": "#F2A0A6",
        "inputborder": "#333A50", "hoverborder": "#4A5273",
        "focus": "#7C8CFF", "accent": "#6F7DFF",
        "accenthover": "#8290FF", "accentpressed": "#5E6BEA",
        "selected": "#343C66", "selectedtext": "#FFFFFF",
        "btn": "#2A3042", "btnborder": "#353C52",
        "btnhover": "#333A52", "btnpressed": "#262B3C",
        "dangerborder": "#5A3A40", "scroll": "#343B52",
        "gesture": "#A9B4FF",
    },
}


# =========================================================
# ÍCONES DAS SETAS DOS SPINBOXES
# =========================================================

_ARROW_CACHE = {}


def make_arrow_icons(theme, color):
    """Gera (uma vez por tema) os PNGs das setas e devolve os caminhos."""

    if theme in _ARROW_CACHE:
        return _ARROW_CACHE[theme]

    folder = Path(tempfile.gettempdir()) / "handify_icons"
    folder.mkdir(exist_ok=True)

    paths = {}

    for name in ("up", "down"):

        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(QColor(color))
        pen.setWidthF(2.4)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)

        c = pixmap.rect().center()

        if name == "up":
            points = [c + QPoint(-6, 3), c + QPoint(0, -3), c + QPoint(6, 3)]
        else:
            points = [c + QPoint(-6, -3), c + QPoint(0, 3), c + QPoint(6, -3)]

        painter.drawPolyline(points)
        painter.end()

        path = folder / f"{theme}_{name}.png"
        pixmap.save(str(path), "PNG")

        paths[name] = path.as_posix()

    _ARROW_CACHE[theme] = paths
    return paths


def build_style(theme):
    """Gera a folha de estilo (QSS) para o tema 'light' ou 'dark'."""

    palette = dict(PALETTES.get(theme, PALETTES["light"]))

    arrows = make_arrow_icons(theme, palette["muted"])
    palette["uparrow"] = arrows["up"]
    palette["downarrow"] = arrows["down"]

    style = STYLE_TEMPLATE

    # Nomes maiores primeiro (@selectedtext antes de @selected, etc.)
    for key in sorted(palette, key=len, reverse=True):
        style = style.replace("@" + key, palette[key])

    return style


def make_card(title=None, subtitle=None):
    """Cria um painel arredondado e devolve (frame, layout)."""

    frame = QFrame()
    frame.setObjectName("card")

    layout = QVBoxLayout(frame)
    layout.setContentsMargins(18, 16, 18, 18)
    layout.setSpacing(12)

    if title:
        label = QLabel(title)
        label.setObjectName("cardTitle")
        layout.addWidget(label)

    if subtitle:
        hint = QLabel(subtitle)
        hint.setObjectName("muted")
        hint.setWordWrap(True)
        layout.addWidget(hint)

    return frame, layout


# =========================================================
# PRÉ-VISUALIZAÇÃO DA MÃO
# =========================================================

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
]


def sample_to_points(sample):
    """Converte uma amostra em 21 pares (x, y). Devolve [] se não reconhecer."""

    if sample is None:
        return []

    try:
        sample = list(sample)

        if not sample:
            return []

        if isinstance(sample[0], (list, tuple)):
            points = [(float(p[0]), float(p[1])) for p in sample]

        else:
            flat = [float(v) for v in sample]

            if len(flat) == 63:
                stride = 3
            elif len(flat) == 42:
                stride = 2
            else:
                return []

            points = [
                (flat[i], flat[i + 1])
                for i in range(0, len(flat), stride)
            ]

    except (TypeError, ValueError, IndexError):
        return []

    return points if len(points) == 21 else []


class HandPreview(QWidget):
    """Desenha o esqueleto da mão a partir de uma amostra."""

    def __init__(self, parent=None):

        super().__init__(parent)

        self.points = []
        self.line_color = QColor("#8B93AA")
        self.dot_color = QColor("#6F7DFF")

        self.setMinimumSize(160, 160)

    def set_colors(self, line, dot):

        self.line_color = QColor(line)
        self.dot_color = QColor(dot)
        self.update()

    def set_sample(self, sample):

        self.points = sample_to_points(sample)
        self.update()

    def paintEvent(self, event):

        if not self.points:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]

        min_x, min_y = min(xs), min(ys)

        span_x = (max(xs) - min_x) or 1.0
        span_y = (max(ys) - min_y) or 1.0

        margin = 14
        size = min(self.width(), self.height()) - 2 * margin
        scale = size / max(span_x, span_y)

        offset_x = (self.width() - span_x * scale) / 2
        offset_y = (self.height() - span_y * scale) / 2

        mapped = [
            QPointF(
                offset_x + (x - min_x) * scale,
                offset_y + (y - min_y) * scale,
            )
            for x, y in self.points
        ]

        pen = QPen(self.line_color)
        pen.setWidthF(2.2)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        for a, b in HAND_CONNECTIONS:
            painter.drawLine(mapped[a], mapped[b])

        painter.setPen(Qt.NoPen)
        painter.setBrush(self.dot_color)

        for point in mapped:
            painter.drawEllipse(point, 3.5, 3.5)

        painter.end()


class MainWindow(QMainWindow):

    # Rótulo da ação -> campos relevantes no formulário
    ACTION_FIELDS = {
        "Tecla": ["key"],
        "Combinação": ["keys"],
        "Sequência": ["sequence"],
        "Clique": ["button"],
        "Duplo clique": ["button"],
        "Rolagem": ["amount"],
        "Rolagem horizontal": ["amount"],
        "Comando especial": ["special"],
    }

    def __init__(self):

        super().__init__()

        self.setWindowTitle("SIGCD — Gestos personalizados")
        self.resize(1240, 760)
        self.setMinimumSize(1000, 640)

        self.settings = QSettings("handify", "sigcd")
        self.theme = self.settings.value("theme", "light")
        self.apply_theme(self.theme, save=False)

        self.config = ConfigManager()
        self.executor = ActionExecutor()
        self.recognizer = GestureRecognizer()
        self.controller = GestureController(self.config, self.executor)

        self.camera = cv2.VideoCapture(0, cv2.CAP_V4L2)

        if not self.camera.isOpened():
            self.camera = cv2.VideoCapture(0)

        self.current_sample = None

        self.build_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process_frame)
        self.timer.start(30)

    # =====================================================
    # INTERFACE
    # =====================================================

    def build_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(20)

        root.addLayout(self.build_camera_panel(), 3)
        root.addWidget(self.build_side_panel(), 2)

        self.refresh_list()
        self.update_action_fields()
        self.apply_theme(self.theme, save=False)

    # -----------------------------------------------------
    # Câmera
    # -----------------------------------------------------

    def build_camera_panel(self):

        left = QVBoxLayout()
        left.setSpacing(14)

        self.video = QLabel("Aguardando câmera…")
        self.video.setObjectName("video")
        self.video.setMinimumSize(640, 480)
        self.video.setAlignment(Qt.AlignCenter)

        left.addWidget(self.video, 1)

        # Gesto detectado

        info, info_layout = make_card()

        caption = QLabel("Gesto detectado")
        caption.setObjectName("muted")

        self.detected = QLabel("")
        self.detected.setObjectName("gestureName")
        self.detected.setMinimumHeight(32)
        self.detected.setToolTip("Identificação do gesto realizado")

        top = QHBoxLayout()
        top.addWidget(caption)
        top.addStretch()

        self.confidence = QLabel("")
        self.confidence.setObjectName("muted")
        top.addWidget(self.confidence)

        self.confidence_bar = QProgressBar()
        self.confidence_bar.setRange(0, 100)
        self.confidence_bar.setValue(0)
        self.confidence_bar.setTextVisible(False)

        info_layout.setSpacing(6)
        info_layout.addLayout(top)
        info_layout.addWidget(self.detected)
        info_layout.addWidget(self.confidence_bar)

        left.addWidget(info)

        self.capture_button = QPushButton("Capturar amostra do gesto atual")
        self.capture_button.setObjectName("primary")
        self.capture_button.setCursor(Qt.PointingHandCursor)
        self.capture_button.clicked.connect(self.capture_gesture)

        left.addWidget(self.capture_button)

        return left

    # -----------------------------------------------------
    # Painel lateral
    # -----------------------------------------------------

    def build_side_panel(self):

        content = QWidget()

        right = QVBoxLayout(content)
        right.setContentsMargins(0, 0, 8, 0)
        right.setSpacing(14)

        self.theme_button = QPushButton()
        self.theme_button.setCursor(Qt.PointingHandCursor)
        self.theme_button.setToolTip("Alternar entre modo claro e escuro")
        self.theme_button.clicked.connect(self.toggle_theme)

        header = QHBoxLayout()
        header.addStretch()
        header.addWidget(self.theme_button)

        right.addLayout(header)
        right.addWidget(self.build_gesture_card())
        right.addWidget(self.build_form_card())

        save_button = QPushButton("Salvar configuração")
        save_button.setObjectName("primary")
        save_button.setCursor(Qt.PointingHandCursor)
        save_button.clicked.connect(self.save_gesture)

        test_button = QPushButton("Testar ação")
        test_button.setCursor(Qt.PointingHandCursor)
        test_button.clicked.connect(self.test_action)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        actions.addWidget(test_button)
        actions.addWidget(save_button, 1)

        right.addLayout(actions)

        self.status = QLabel("Pronto.")
        self.status.setObjectName("status")
        self.status.setWordWrap(True)

        right.addWidget(self.status)
        right.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(content)
        scroll.setMinimumWidth(380)

        return scroll

    def build_gesture_card(self):

        card, layout = make_card("Gestos cadastrados")

        self.gesture_combo = QComboBox()
        self.gesture_combo.setCursor(Qt.PointingHandCursor)
        self.gesture_combo.setToolTip("Selecione um gesto cadastrado")
        self.gesture_combo.currentIndexChanged.connect(
            self.on_gesture_changed
        )

        layout.addWidget(self.gesture_combo)

        # Pré-visualização da amostra salva

        preview_caption = QLabel("Amostra mais recente")
        preview_caption.setObjectName("muted")
        layout.addWidget(preview_caption)

        self.preview = HandPreview()
        layout.addWidget(self.preview)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)

        new_button = QPushButton("Novo gesto")
        new_button.setCursor(Qt.PointingHandCursor)
        new_button.clicked.connect(self.new_gesture)

        delete_button = QPushButton("Excluir")
        delete_button.setObjectName("danger")
        delete_button.setCursor(Qt.PointingHandCursor)
        delete_button.clicked.connect(self.delete_gesture)

        buttons.addWidget(new_button, 1)
        buttons.addWidget(delete_button)

        layout.addLayout(buttons)

        return card

    def build_form_card(self):

        card, layout = make_card("Configuração do gesto")

        self.form = QFormLayout()
        self.form.setHorizontalSpacing(14)
        self.form.setVerticalSpacing(10)
        self.form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        form = self.form

        # Nome

        self.name_edit = QLineEdit()
        form.addRow("Nome", self.name_edit)

        # Ação

        self.action_combo = QComboBox()
        self.action_combo.addItems(list(self.ACTION_FIELDS.keys()))
        self.action_combo.currentTextChanged.connect(
            self.update_action_fields
        )
        form.addRow("Ação", self.action_combo)

        # Tecla

        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("enter, space, f5…")
        form.addRow("Tecla", self.key_edit)

        # Combinação

        self.keys_edit = QLineEdit()
        self.keys_edit.setPlaceholderText("ctrl+shift+esc")
        form.addRow("Combinação", self.keys_edit)

        # Sequência

        self.sequence_edit = QLineEdit()
        self.sequence_edit.setPlaceholderText(
            "ctrl+c | delay:0.2 | ctrl+v"
        )
        self.sequence_edit.setToolTip(
            "Separe os passos com |. Use delay:segundos para pausas."
        )
        form.addRow("Sequência", self.sequence_edit)

        # Botão

        self.button_combo = QComboBox()
        self.button_combo.addItems(["left", "right", "middle"])
        form.addRow("Botão", self.button_combo)

        # Duração (usada apenas por 'hold')

        self.duration = QDoubleSpinBox()
        self.duration.setRange(0, 60)
        self.duration.setDecimals(2)
        self.duration.setSuffix(" s")
        self.duration.setValue(1)
        form.addRow("Duração", self.duration)

        # Quantidade

        self.amount_spin = QSpinBox()
        self.amount_spin.setRange(-1000, 1000)
        self.amount_spin.setValue(50)
        self.amount_spin.setToolTip(
            "Valores negativos rolam no sentido contrário."
        )
        form.addRow("Rolagem", self.amount_spin)

        # Especial

        self.special_combo = QComboBox()
        self.special_combo.addItems(["screenshot"])
        form.addRow("Especial", self.special_combo)

        layout.addLayout(form)

        # Divisor

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setObjectName("divider")
        layout.addWidget(divider)

        # Ajustes gerais

        general = QFormLayout()
        general.setHorizontalSpacing(14)
        general.setVerticalSpacing(10)
        general.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.min_confidence = QSpinBox()
        self.min_confidence.setRange(0, 100)
        self.min_confidence.setSingleStep(5)
        self.min_confidence.setSuffix(" %")
        self.min_confidence.setValue(65)
        self.min_confidence.setToolTip(
            "Só executa a ação acima desta confiança."
        )
        general.addRow("Confiança mínima", self.min_confidence)

        self.cooldown = QDoubleSpinBox()
        self.cooldown.setRange(0, 60)
        self.cooldown.setDecimals(2)
        self.cooldown.setSuffix(" s")
        self.cooldown.setValue(0.5)
        self.cooldown.setToolTip(
            "Tempo de espera antes de repetir a ação."
        )
        general.addRow("Cooldown", self.cooldown)

        self.enabled = QCheckBox("Gesto ativado")
        self.enabled.setChecked(True)
        general.addRow(self.enabled)

        layout.addLayout(general)

        # Campos que podem ser mostrados/ocultados

        self.field_widgets = {
            "key": self.key_edit,
            "keys": self.keys_edit,
            "sequence": self.sequence_edit,
            "button": self.button_combo,
            "amount": self.amount_spin,
            "special": self.special_combo,
        }

        return card

    # =====================================================
    # TEMA
    # =====================================================

    def apply_theme(self, theme, save=True):

        self.theme = theme
        self.setStyleSheet(build_style(theme))

        if hasattr(self, "theme_button"):
            self.theme_button.setText(
                "Modo escuro" if theme == "light" else "Modo claro"
            )

        if hasattr(self, "preview"):
            palette = PALETTES.get(theme, PALETTES["light"])
            self.preview.set_colors(palette["muted"], palette["accent"])

        if save:
            self.settings.setValue("theme", theme)

    def toggle_theme(self):

        self.apply_theme(
            "dark" if self.theme == "light" else "light"
        )

    # =====================================================
    # CAMPOS CONTEXTUAIS
    # =====================================================

    def update_action_fields(self, *_):
        """Mostra só os campos que a ação escolhida realmente usa."""

        visible = self.ACTION_FIELDS.get(
            self.action_combo.currentText(),
            []
        )

        for name, widget in self.field_widgets.items():

            show = name in visible

            widget.setVisible(show)

            label = self.form.labelForField(widget)

            if label:
                label.setVisible(show)

        # "Duração" só existe para 'hold', que não está na lista.
        self.duration.setVisible(False)

        label = self.form.labelForField(self.duration)

        if label:
            label.setVisible(False)

    # =====================================================
    # STATUS
    # =====================================================

    def set_status(self, text, kind="info"):

        self.status.setText(text)
        self.status.setProperty("kind", kind)

        # Reaplica o estilo para refletir a nova propriedade
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)

    # =====================================================
    # LISTA
    # =====================================================

    def selected_id(self):

        # None quando o dropdown está vazio
        return self.gesture_combo.currentData()

    def refresh_list(self):

        current = self.selected_id()

        self.gesture_combo.blockSignals(True)
        self.gesture_combo.clear()

        for gesture_id, gesture in self.config.all_gestures().items():

            self.gesture_combo.addItem(
                gesture.get("name") or gesture_id,
                gesture_id
            )

        index = self.gesture_combo.findData(current) if current else -1

        if index < 0 and self.gesture_combo.count():
            index = 0

        self.gesture_combo.setCurrentIndex(index)
        self.gesture_combo.blockSignals(False)

        self.load_gesture(self.selected_id())

    def on_gesture_changed(self, index):

        self.load_gesture(self.gesture_combo.itemData(index))

    # =====================================================
    # NOVO GESTO
    # =====================================================

    def new_gesture(self):

        dialog = QInputDialog(self)
        dialog.setStyleSheet(build_style(self.theme))
        dialog.setWindowTitle("Novo gesto")
        dialog.setLabelText("Nome do gesto:")
        dialog.setTextValue("")
        dialog.setOkButtonText("Criar")
        dialog.setCancelButtonText("Cancelar")
        dialog.setMinimumWidth(380)

        if dialog.exec() != QInputDialog.Accepted:
            return

        name = dialog.textValue().strip()

        if not name:
            return

        gesture_id = uuid.uuid4().hex

        self.config.set(
            gesture_id,
            {
                "name": name,
                "samples": [],
                "enabled": True,
                "min_confidence": 0.65,
                "cooldown": 0.5,
                "action": {
                    "type": "key",
                    "key": "enter"
                }
            }
        )

        self.refresh_list()

        self.gesture_combo.setCurrentIndex(
            self.gesture_combo.findData(gesture_id)
        )

        self.set_status(
            "Gesto criado. Mostre a mão à câmera e capture algumas amostras.",
            "ok"
        )

    # =====================================================
    # EXCLUIR
    # =====================================================

    def delete_gesture(self):

        gesture_id = self.selected_id()

        if not gesture_id:
            return

        self.config.remove(gesture_id)
        self.refresh_list()

        self.set_status("Gesto removido.", "warn")

    # =====================================================
    # CAPTURAR
    # =====================================================

    def capture_gesture(self):

        gesture_id = self.selected_id()

        if not gesture_id:

            QMessageBox.warning(
                self,
                "Nenhum gesto",
                "Crie ou selecione um gesto primeiro."
            )

            return

        if self.current_sample is None:

            QMessageBox.warning(
                self,
                "Nenhuma mão",
                "Mostre a mão para a câmera."
            )

            return

        gesture = self.config.get(gesture_id)

        gesture.setdefault("samples", [])
        gesture["samples"].append(self.current_sample)

        self.config.set(gesture_id, gesture)

        self.preview.set_sample(self.current_sample)

        self.set_status(
            f"Amostras capturadas: {len(gesture['samples'])}",
            "ok"
        )

    # =====================================================
    # CARREGAR
    # =====================================================

    def load_gesture(self, gesture_id):

        if not gesture_id:
            self.preview.set_sample(None)
            return

        gesture = self.config.get(gesture_id)

        if not gesture:
            self.preview.set_sample(None)
            return

        self.name_edit.setText(gesture.get("name", ""))
        self.enabled.setChecked(gesture.get("enabled", True))

        self.min_confidence.setValue(
            round(float(gesture.get("min_confidence", 0.65)) * 100)
        )

        self.cooldown.setValue(
            float(gesture.get("cooldown", 0.5))
        )

        action = gesture.get("action", {})
        action_type = action.get("type")

        labels = {
            "key": "Tecla",
            "hotkey": "Combinação",
            "sequence": "Sequência",
            "click": "Clique",
            "double_click": "Duplo clique",
            "scroll": "Rolagem",
            "hscroll": "Rolagem horizontal",
            "special": "Comando especial"
        }

        if action_type in labels:
            self.action_combo.setCurrentText(labels[action_type])

        self.key_edit.setText(action.get("key", ""))

        self.keys_edit.setText("+".join(action.get("keys", [])))

        self.sequence_edit.setText(
            self.sequence_to_text(action.get("actions", []))
        )

        self.button_combo.setCurrentText(action.get("button", "left"))

        self.duration.setValue(float(action.get("duration", 1)))

        self.amount_spin.setValue(int(action.get("amount", 5)))

        self.special_combo.setCurrentText(
            action.get("command", "screenshot")
        )

        samples = gesture.get("samples", [])
        self.preview.set_sample(samples[-1] if samples else None)

        self.update_action_fields()

    # =====================================================
    # SEQUÊNCIA → TEXTO
    # =====================================================

    def sequence_to_text(self, actions):

        parts = []

        for action in actions:

            action_type = action.get("type")

            if action_type == "delay":
                parts.append(f"delay:{action.get('seconds', 0)}")

            elif action_type == "key":
                parts.append(action.get("key", ""))

            elif action_type == "hotkey":
                parts.append("+".join(action.get("keys", [])))

        return " | ".join(parts)

    # =====================================================
    # CONSTRUIR AÇÃO
    # =====================================================

    def build_action(self):

        label = self.action_combo.currentText()

        if label == "Tecla":

            return {
                "type": "key",
                "key": self.key_edit.text().strip().lower()
            }

        if label == "Combinação":

            keys = [
                key.strip().lower()
                for key in self.keys_edit.text().split("+")
                if key.strip()
            ]

            return {"type": "hotkey", "keys": keys}

        if label == "Sequência":

            actions = []

            for part in self.sequence_edit.text().split("|"):

                part = part.strip()

                if not part:
                    continue

                if part.startswith("delay:"):

                    seconds = float(part.split(":", 1)[1])

                    actions.append(
                        {"type": "delay", "seconds": seconds}
                    )

                else:

                    keys = [
                        key.strip().lower()
                        for key in part.split("+")
                        if key.strip()
                    ]

                    if len(keys) == 1:
                        actions.append(
                            {"type": "key", "key": keys[0]}
                        )

                    else:
                        actions.append(
                            {"type": "hotkey", "keys": keys}
                        )

            return {"type": "sequence", "actions": actions}

        if label == "Clique":

            return {
                "type": "click",
                "button": self.button_combo.currentText()
            }

        if label == "Duplo clique":

            return {
                "type": "double_click",
                "button": self.button_combo.currentText()
            }

        if label == "Pressionar e segurar":

            return {
                "type": "hold",
                "key": self.key_edit.text().strip().lower(),
                "duration": self.duration.value()
            }

        if label == "Rolagem":

            return {
                "type": "scroll",
                "amount": self.amount_spin.value()
            }

        if label == "Rolagem horizontal":

            return {
                "type": "hscroll",
                "amount": self.amount_spin.value()
            }

        if label == "Comando especial":

            return {
                "type": "special",
                "command": self.special_combo.currentText()
            }

        raise ValueError("Ação inválida.")

    # =====================================================
    # SALVAR
    # =====================================================

    def save_gesture(self):

        gesture_id = self.selected_id()

        if not gesture_id:

            QMessageBox.warning(
                self,
                "Nenhum gesto",
                "Crie ou selecione um gesto."
            )

            return

        try:
            action = self.build_action()

        except Exception as exc:

            QMessageBox.critical(self, "Erro", str(exc))
            return

        gesture = self.config.get(gesture_id)

        gesture["name"] = self.name_edit.text().strip() or gesture_id
        gesture["enabled"] = self.enabled.isChecked()
        gesture["min_confidence"] = self.min_confidence.value() / 100
        gesture["cooldown"] = self.cooldown.value()
        gesture["action"] = action

        self.config.set(gesture_id, gesture)

        self.refresh_list()

        self.set_status("Configuração salva.", "ok")

    # =====================================================
    # TESTAR
    # =====================================================

    def test_action(self):

        try:

            self.executor.execute(self.build_action())

            self.set_status("Ação executada.", "ok")

        except Exception as exc:

            QMessageBox.critical(self, "Erro", str(exc))

    # =====================================================
    # FRAME
    # =====================================================

    def process_frame(self):

        ok, frame = self.camera.read()

        if not ok:
            return

        gesture_id, confidence, sample = self.recognizer.recognize(
            frame,
            self.config.all_gestures()
        )

        self.current_sample = sample

        if gesture_id:

            gesture = self.config.get(gesture_id)
            name = (gesture.get("name") or "").strip() or "Gesto sem nome"

            self.detected.setText(name)
            self.confidence.setText(f"{confidence:.0%}")
            self.confidence_bar.setValue(int(confidence * 100))

            try:

                executed = self.controller.process(
                    gesture_id,
                    confidence
                )

                if executed:
                    self.set_status(f"Executado: {name}", "ok")

            except Exception as exc:

                self.set_status(f"Erro: {exc}", "error")

        else:

            self.detected.setText("")
            self.confidence.setText("")
            self.confidence_bar.setValue(0)

        # Mostrar câmera

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        height, width, channels = rgb.shape

        image = QImage(
            rgb.data,
            width,
            height,
            channels * width,
            QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(image)

        self.video.setPixmap(
            pixmap.scaled(
                self.video.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    # =====================================================
    # FECHAR
    # =====================================================

    def closeEvent(self, event):

        self.timer.stop()
        self.camera.release()
        self.recognizer.close()

        event.accept()