import uuid

import cv2

from PySide6.QtCore import (
    QTimer,
    Qt
)

from PySide6.QtGui import (
    QImage,
    QPixmap
)

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
    QCheckBox,
    QGroupBox,
    QFormLayout,
    QMessageBox,
    QInputDialog
)

from handify.config.manager import ConfigManager
from handify.actions.executor import ActionExecutor
from handify.recognition.gesture_recognizer import GestureRecognizer
from handify.recognition.controller import GestureController


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "SIGCD — Gestos personalizados"
        )

        self.resize(
            1200,
            720
        )

        self.config = ConfigManager()

        self.executor = ActionExecutor()

        self.recognizer = GestureRecognizer()

        self.controller = GestureController(
            self.config,
            self.executor
        )

        self.camera = cv2.VideoCapture(
            0,
            cv2.CAP_V4L2
        )

        if not self.camera.isOpened():

            self.camera = cv2.VideoCapture(0)

        self.current_sample = None

        self.build_ui()

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.process_frame
        )

        self.timer.start(30)

    # =====================================================
    # INTERFACE
    # =====================================================

    def build_ui(self):

        central = QWidget()

        self.setCentralWidget(
            central
        )

        root = QHBoxLayout(
            central
        )

        # =================================================
        # CÂMERA
        # =================================================

        left = QVBoxLayout()

        self.video = QLabel(
            "Câmera"
        )

        self.video.setMinimumSize(
            640,
            480
        )

        self.video.setAlignment(
            Qt.AlignCenter
        )

        self.video.setStyleSheet(
            """
            background: #111;
            color: #aaa;
            """
        )

        left.addWidget(
            self.video
        )

        self.detected = QLabel(
            "Gesto: —"
        )

        self.confidence = QLabel(
            "Confiança: —"
        )

        left.addWidget(
            self.detected
        )

        left.addWidget(
            self.confidence
        )

        self.capture_button = QPushButton(
            "Capturar gesto atual"
        )

        self.capture_button.clicked.connect(
            self.capture_gesture
        )

        left.addWidget(
            self.capture_button
        )

        root.addLayout(
            left,
            2
        )

        # =================================================
        # DIREITA
        # =================================================

        right = QVBoxLayout()

        # =================================================
        # GESTOS
        # =================================================

        gesture_group = QGroupBox(
            "Gestos cadastrados"
        )

        gesture_layout = QVBoxLayout(
            gesture_group
        )

        self.gesture_list = QListWidget()

        self.gesture_list.currentItemChanged.connect(
            self.load_selected
        )

        gesture_layout.addWidget(
            self.gesture_list
        )

        buttons = QHBoxLayout()

        new_button = QPushButton(
            "Novo"
        )

        new_button.clicked.connect(
            self.new_gesture
        )

        delete_button = QPushButton(
            "Excluir"
        )

        delete_button.clicked.connect(
            self.delete_gesture
        )

        buttons.addWidget(
            new_button
        )

        buttons.addWidget(
            delete_button
        )

        gesture_layout.addLayout(
            buttons
        )

        right.addWidget(
            gesture_group
        )

        # =================================================
        # CONFIGURAÇÃO
        # =================================================

        form_group = QGroupBox(
            "Configuração do gesto"
        )

        form = QFormLayout(
            form_group
        )

        # Nome

        self.name_edit = QLineEdit()

        form.addRow(
            "Nome:",
            self.name_edit
        )

        # Ação

        self.action_combo = QComboBox()

        self.action_combo.addItems(
            [
                "Tecla",
                "Combinação",
                "Sequência",
                "Clique",
                "Duplo clique",
                "Pressionar e segurar",
                "Mover mouse",
                "Mover mouse para posição",
                "Rolagem",
                "Rolagem horizontal",
                "Comando especial"
            ]
        )

        form.addRow(
            "Ação:",
            self.action_combo
        )

        # Tecla

        self.key_edit = QLineEdit()

        self.key_edit.setPlaceholderText(
            "enter, space, f5..."
        )

        form.addRow(
            "Tecla:",
            self.key_edit
        )

        # Combinação

        self.keys_edit = QLineEdit()

        self.keys_edit.setPlaceholderText(
            "ctrl+shift+esc"
        )

        form.addRow(
            "Combinação:",
            self.keys_edit
        )

        # Sequência

        self.sequence_edit = QLineEdit()

        self.sequence_edit.setPlaceholderText(
            "ctrl+c | delay:0.2 | ctrl+v"
        )

        form.addRow(
            "Sequência:",
            self.sequence_edit
        )

        # Botão

        self.button_combo = QComboBox()

        self.button_combo.addItems(
            [
                "left",
                "right",
                "middle"
            ]
        )

        form.addRow(
            "Botão:",
            self.button_combo
        )

        # Duração

        self.duration = QDoubleSpinBox()

        self.duration.setRange(
            0,
            60
        )

        self.duration.setDecimals(
            2
        )

        self.duration.setValue(
            1
        )

        form.addRow(
            "Duração:",
            self.duration
        )

        # X

        self.x_spin = QSpinBox()

        self.x_spin.setRange(
            -10000,
            10000
        )

        form.addRow(
            "X:",
            self.x_spin
        )

        # Y

        self.y_spin = QSpinBox()

        self.y_spin.setRange(
            -10000,
            10000
        )

        form.addRow(
            "Y:",
            self.y_spin
        )

        # Quantidade

        self.amount_spin = QSpinBox()

        self.amount_spin.setRange(
            -1000,
            1000
        )

        self.amount_spin.setValue(
            5
        )

        form.addRow(
            "Quantidade:",
            self.amount_spin
        )

        # Especial

        self.special_combo = QComboBox()

        self.special_combo.addItems(
            [
                "screenshot"
            ]
        )

        form.addRow(
            "Especial:",
            self.special_combo
        )

        # Ativado

        self.enabled = QCheckBox(
            "Ativado"
        )

        self.enabled.setChecked(
            True
        )

        form.addRow(
            self.enabled
        )

        # Confiança

        self.min_confidence = QDoubleSpinBox()

        self.min_confidence.setRange(
            0,
            1
        )

        self.min_confidence.setDecimals(
            2
        )

        self.min_confidence.setSingleStep(
            0.05
        )

        self.min_confidence.setValue(
            0.65
        )

        form.addRow(
            "Confiança mínima:",
            self.min_confidence
        )

        # Cooldown

        self.cooldown = QDoubleSpinBox()

        self.cooldown.setRange(
            0,
            60
        )

        self.cooldown.setDecimals(
            2
        )

        self.cooldown.setValue(
            0.5
        )

        form.addRow(
            "Cooldown:",
            self.cooldown
        )

        right.addWidget(
            form_group
        )

        # =================================================
        # BOTÕES
        # =================================================

        save_button = QPushButton(
            "Salvar configuração"
        )

        save_button.clicked.connect(
            self.save_gesture
        )

        right.addWidget(
            save_button
        )

        test_button = QPushButton(
            "Testar ação"
        )

        test_button.clicked.connect(
            self.test_action
        )

        right.addWidget(
            test_button
        )

        # =================================================
        # STATUS
        # =================================================

        self.status = QLabel(
            "Pronto."
        )

        right.addWidget(
            self.status
        )

        right.addStretch()

        root.addLayout(
            right,
            1
        )

        self.refresh_list()

    # =====================================================
    # LISTA
    # =====================================================

    def selected_id(self):

        item = self.gesture_list.currentItem()

        if not item:
            return None

        return item.data(
            Qt.UserRole
        )

    def refresh_list(self):

        current = self.selected_id()

        self.gesture_list.clear()

        for gesture_id, gesture in (
            self.config.all_gestures().items()
        ):

            item = QListWidgetItem(
                gesture.get(
                    "name",
                    gesture_id
                )
            )

            item.setData(
                Qt.UserRole,
                gesture_id
            )

            self.gesture_list.addItem(
                item
            )

            if gesture_id == current:

                self.gesture_list.setCurrentItem(
                    item
                )

        if (
            self.gesture_list.count()
            and self.gesture_list.currentRow() < 0
        ):

            self.gesture_list.setCurrentRow(
                0
            )

    # =====================================================
    # NOVO GESTO
    # =====================================================

    def new_gesture(self):

        name, ok = QInputDialog.getText(
            self,
            "Novo gesto",
            "Nome do gesto:"
        )

        if not ok:
            return

        name = name.strip()

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

        for index in range(
            self.gesture_list.count()
        ):

            item = self.gesture_list.item(
                index
            )

            if item.data(
                Qt.UserRole
            ) == gesture_id:

                self.gesture_list.setCurrentRow(
                    index
                )

                break

        self.status.setText(
            "Gesto criado. Mostre o gesto e capture algumas amostras."
        )

    # =====================================================
    # EXCLUIR
    # =====================================================

    def delete_gesture(self):

        gesture_id = self.selected_id()

        if not gesture_id:
            return

        self.config.remove(
            gesture_id
        )

        self.refresh_list()

        self.status.setText(
            "Gesto removido."
        )

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

        gesture = self.config.get(
            gesture_id
        )

        gesture.setdefault(
            "samples",
            []
        )

        gesture["samples"].append(
            self.current_sample
        )

        self.config.set(
            gesture_id,
            gesture
        )

        self.status.setText(
            f"Amostras capturadas: "
            f"{len(gesture['samples'])}"
        )

    # =====================================================
    # CARREGAR
    # =====================================================

    def load_selected(
        self,
        current,
        previous=None
    ):

        if not current:
            return

        gesture_id = current.data(
            Qt.UserRole
        )

        gesture = self.config.get(
            gesture_id
        )

        if not gesture:
            return

        self.name_edit.setText(
            gesture.get(
                "name",
                ""
            )
        )

        self.enabled.setChecked(
            gesture.get(
                "enabled",
                True
            )
        )

        self.min_confidence.setValue(
            float(
                gesture.get(
                    "min_confidence",
                    0.65
                )
            )
        )

        self.cooldown.setValue(
            float(
                gesture.get(
                    "cooldown",
                    0.5
                )
            )
        )

        action = gesture.get(
            "action",
            {}
        )

        action_type = action.get(
            "type"
        )

        labels = {
            "key": "Tecla",
            "hotkey": "Combinação",
            "sequence": "Sequência",
            "click": "Clique",
            "double_click": "Duplo clique",
            "hold": "Pressionar e segurar",
            "move_relative": "Mover mouse",
            "move_absolute": "Mover mouse para posição",
            "scroll": "Rolagem",
            "hscroll": "Rolagem horizontal",
            "special": "Comando especial"
        }

        if action_type in labels:

            self.action_combo.setCurrentText(
                labels[action_type]
            )

        self.key_edit.setText(
            action.get(
                "key",
                ""
            )
        )

        self.keys_edit.setText(
            "+".join(
                action.get(
                    "keys",
                    []
                )
            )
        )

        self.sequence_edit.setText(
            self.sequence_to_text(
                action.get(
                    "actions",
                    []
                )
            )
        )

        self.button_combo.setCurrentText(
            action.get(
                "button",
                "left"
            )
        )

        self.duration.setValue(
            float(
                action.get(
                    "duration",
                    1
                )
            )
        )

        self.x_spin.setValue(
            int(
                action.get(
                    "x",
                    0
                )
            )
        )

        self.y_spin.setValue(
            int(
                action.get(
                    "y",
                    0
                )
            )
        )

        self.amount_spin.setValue(
            int(
                action.get(
                    "amount",
                    5
                )
            )
        )

        self.special_combo.setCurrentText(
            action.get(
                "command",
                "screenshot"
            )
        )

    # =====================================================
    # SEQUÊNCIA → TEXTO
    # =====================================================

    def sequence_to_text(
        self,
        actions
    ):

        parts = []

        for action in actions:

            action_type = action.get(
                "type"
            )

            if action_type == "delay":

                parts.append(
                    f"delay:{action.get('seconds', 0)}"
                )

            elif action_type == "key":

                parts.append(
                    action.get(
                        "key",
                        ""
                    )
                )

            elif action_type == "hotkey":

                parts.append(
                    "+".join(
                        action.get(
                            "keys",
                            []
                        )
                    )
                )

        return " | ".join(parts)

    # =====================================================
    # CONSTRUIR AÇÃO
    # =====================================================

    def build_action(self):

        label = self.action_combo.currentText()

        # Tecla

        if label == "Tecla":

            return {
                "type": "key",
                "key": self.key_edit.text()
                .strip()
                .lower()
            }

        # Combinação

        if label == "Combinação":

            keys = [
                key.strip().lower()
                for key in self.keys_edit
                .text()
                .split("+")
                if key.strip()
            ]

            return {
                "type": "hotkey",
                "keys": keys
            }

        # Sequência

        if label == "Sequência":

            actions = []

            for part in (
                self.sequence_edit
                .text()
                .split("|")
            ):

                part = part.strip()

                if not part:
                    continue

                if part.startswith(
                    "delay:"
                ):

                    seconds = float(
                        part.split(
                            ":",
                            1
                        )[1]
                    )

                    actions.append(
                        {
                            "type": "delay",
                            "seconds": seconds
                        }
                    )

                else:

                    keys = [
                        key.strip().lower()
                        for key in part.split("+")
                        if key.strip()
                    ]

                    if len(keys) == 1:

                        actions.append(
                            {
                                "type": "key",
                                "key": keys[0]
                            }
                        )

                    else:

                        actions.append(
                            {
                                "type": "hotkey",
                                "keys": keys
                            }
                        )

            return {
                "type": "sequence",
                "actions": actions
            }

        # Clique

        if label == "Clique":

            return {
                "type": "click",
                "button": self.button_combo.currentText()
            }

        # Duplo clique

        if label == "Duplo clique":

            return {
                "type": "double_click",
                "button": self.button_combo.currentText()
            }

        # Hold

        if label == "Pressionar e segurar":

            return {
                "type": "hold",
                "key": self.key_edit.text()
                .strip()
                .lower(),

                "duration": self.duration.value()
            }

        # Mouse relativo

        if label == "Mover mouse":

            return {
                "type": "move_relative",

                "x": self.x_spin.value(),

                "y": self.y_spin.value(),

                "duration": self.duration.value()
            }

        # Mouse absoluto

        if label == "Mover mouse para posição":

            return {
                "type": "move_absolute",

                "x": self.x_spin.value(),

                "y": self.y_spin.value(),

                "duration": self.duration.value()
            }

        # Scroll

        if label == "Rolagem":

            return {
                "type": "scroll",

                "amount": self.amount_spin.value()
            }

        # Scroll horizontal

        if label == "Rolagem horizontal":

            return {
                "type": "hscroll",

                "amount": self.amount_spin.value()
            }

        # Especial

        if label == "Comando especial":

            return {
                "type": "special",

                "command": self.special_combo.currentText()
            }

        raise ValueError(
            "Ação inválida."
        )

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

        gesture = self.config.get(
            gesture_id
        )

        gesture["name"] = (
            self.name_edit.text().strip()
            or gesture_id
        )

        gesture["enabled"] = (
            self.enabled.isChecked()
        )

        gesture["min_confidence"] = (
            self.min_confidence.value()
        )

        gesture["cooldown"] = (
            self.cooldown.value()
        )

        gesture["action"] = (
            self.build_action()
        )

        self.config.set(
            gesture_id,
            gesture
        )

        self.refresh_list()

        self.status.setText(
            "Configuração salva."
        )

    # =====================================================
    # TESTAR
    # =====================================================

    def test_action(self):

        try:

            action = self.build_action()

            self.executor.execute(
                action
            )

            self.status.setText(
                "Ação executada."
            )

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Erro",
                str(exc)
            )

    # =====================================================
    # FRAME
    # =====================================================

    def process_frame(self):

        ok, frame = self.camera.read()

        if not ok:
            return

        gesture_id, confidence, sample = (
            self.recognizer.recognize(
                frame,
                self.config.all_gestures()
            )
        )

        self.current_sample = sample

        if gesture_id:

            gesture = self.config.get(
                gesture_id
            )

            name = gesture.get(
                "name",
                gesture_id
            )

            self.detected.setText(
                f"Gesto: {name}"
            )

            self.confidence.setText(
                f"Confiança: {confidence:.0%}"
            )

            try:

                executed = (
                    self.controller.process(
                        gesture_id,
                        confidence
                    )
                )

                if executed:

                    self.status.setText(
                        f"Executado: {name}"
                    )

            except Exception as exc:

                self.status.setText(
                    f"Erro: {exc}"
                )

        else:

            self.detected.setText(
                "Gesto: —"
            )

            self.confidence.setText(
                "Confiança: —"
            )

        # =================================================
        # MOSTRAR CÂMERA
        # =================================================

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        height, width, channels = (
            rgb.shape
        )

        image = QImage(
            rgb.data,
            width,
            height,
            channels * width,
            QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(
            image
        )

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