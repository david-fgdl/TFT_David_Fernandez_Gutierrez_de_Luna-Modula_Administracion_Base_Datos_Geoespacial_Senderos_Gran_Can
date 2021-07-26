from PyQt5.Qt import *
from PyQt5 import QtWidgets
from psycopg2 import sql

class showDatos(QMainWindow):
    def __init__(self, connection, tableName, intCol, intRow):
        QMainWindow.__init__(self)
        self.intRow = intRow
        if intCol == 12:
            self.tableType = "camino"
        elif intCol == 8:
            self.tableType = "punto"

        self.conn = connection
        self.tableName = tableName
        self.setupUi(self)

    """
        Función para crear la interfaz de la ventana
    """
    def setupUi(self, form):
        self.centralWidget = QtWidgets.QWidget(form)
        self.centralWidget.setMinimumSize(300, 100)
        form.setCentralWidget(self.centralWidget)
        self.statusbar = QtWidgets.QStatusBar(form)
        form.setStatusBar(self.statusbar)

        self.formLayout = QtWidgets.QFormLayout(self.centralWidget)

        self.labelName = QtWidgets.QLabel("Nombre: ", self.centralWidget)
        self.lineName = QtWidgets.QLineEdit(self.centralWidget)
        self.formLayout.addRow(self.labelName, self.lineName)

        if self.tableType == "camino":
            form.setWindowTitle("Formulario de Caminos")
            self.labeltipo = QtWidgets.QLabel("Tipo: ", self.centralWidget)
            self.comboBoxTipo = QtWidgets.QComboBox(self.centralWidget)
            self.comboBoxTipo.addItems(["Oficial", "Anexo"])
            self.formLayout.addRow(self.labeltipo, self.comboBoxTipo)

            self.labelCalidad = QtWidgets.QLabel("Calidad: ", self.centralWidget)
            self.spinBoxCalidad = QtWidgets.QSpinBox(self.centralWidget)
            self.spinBoxCalidad.setRange(1, 7)
            self.formLayout.addRow(self.labelCalidad, self.spinBoxCalidad)

            self.labelNivel = QtWidgets.QLabel("Nivel: ", self.centralWidget)
            self.spinBoxNivel = QtWidgets.QSpinBox(self.centralWidget)
            self.spinBoxNivel.setRange(1, 5)
            self.formLayout.addRow(self.labelNivel, self.spinBoxNivel)

            self.labelKm = QtWidgets.QLabel("Km: ", self.centralWidget)
            self.spinBoxKm = QtWidgets.QSpinBox(self.centralWidget)
            self.formLayout.addRow(self.labelKm, self.spinBoxKm)

            self.labelTiempo = QtWidgets.QLabel("Tiempo: ", self.centralWidget)
            self.spinBoxTiempo = QtWidgets.QSpinBox(self.centralWidget)
            self.formLayout.addRow(self.labelTiempo, self.spinBoxTiempo)

            self.labelRef = QtWidgets.QLabel("Ref: ", self.centralWidget)
            self.lineRef = QtWidgets.QLineEdit(self.centralWidget)
            self.formLayout.addRow(self.labelRef, self.lineRef)

            self.labelBici = QtWidgets.QLabel("Bicicleta: ", self.centralWidget)
            self.radioBtnOn = QtWidgets.QRadioButton("Disponible", self.centralWidget)
            self.radioBtnOff = QtWidgets.QRadioButton("No disponible", self.centralWidget)
            self.radioBtnOff.setChecked(True)
            self.btnLayout = QHBoxLayout()
            self.btnLayout.addWidget(self.radioBtnOn)
            self.btnLayout.addWidget(self.radioBtnOff)
            self.formLayout.addRow(self.labelBici, self.btnLayout)

        elif self.tableType == "punto":
            form.setWindowTitle("Formulario de Punto de red")
            self.labelZona = QtWidgets.QLabel("Zona: ", self.centralWidget)
            self.comboBoxZona = QtWidgets.QComboBox(self.centralWidget)
            self.comboBoxZona.addItems(["Centro", "Norte", "Sur", "Este", "Oeste", "Noreste", "Noroeste", "Sureste",
                                        "Suroeste", "Centro Norte", "Centro Sur", "Centro Este", "Centro Oeste",
                                        "Centro Noreste", "Centro Noroeste", "Centro Sureste", "Centro Suroeste"])

            self.formLayout.addRow(self.labelZona, self.comboBoxZona)

            self.labelPunto = QtWidgets.QLabel("Punto: ", self.centralWidget)
            self.spinBoxPunto = QtWidgets.QSpinBox(self.centralWidget)
            self.spinBoxPunto.setMinimum(1)
            self.formLayout.addRow(self.labelPunto, self.spinBoxPunto)

            self.labelMunicipio = QtWidgets.QLabel("Municipio: ", self.centralWidget)
            self.lineMunicipio = QtWidgets.QLineEdit(self.centralWidget)
            self.formLayout.addRow(self.labelMunicipio, self.lineMunicipio)

            self.labelMovilidad = QtWidgets.QLabel("Movilidad: ", self.centralWidget)
            self.lineMovilidad = QtWidgets.QLineEdit(self.centralWidget)
            self.formLayout.addRow(self.labelMovilidad, self.lineMovilidad)

            self.labelAparcamiento = QtWidgets.QLabel("Aparcamiento: ", self.centralWidget)
            self.radioBtnOn = QtWidgets.QRadioButton("Disponible", self.centralWidget)
            self.radioBtnOff = QtWidgets.QRadioButton("No disponible",self.centralWidget)
            self.radioBtnOff.setChecked(True)
            self.btnLayout = QHBoxLayout()
            self.btnLayout.addWidget(self.radioBtnOn)
            self.btnLayout.addWidget(self.radioBtnOff)
            self.formLayout.addRow(self.labelAparcamiento, self.btnLayout)

        self.buttonBox = QtWidgets.QDialogButtonBox(self.centralWidget)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.formLayout.addRow(self.buttonBox)
        self.buttonBox.accepted.connect(self.addRow)
        self.buttonBox.rejected.connect(self.close)

        form.resize(form.sizeHint())

    """
        Funcion para añadir entrada en un tabla
    """
    def addRow(self):
        id = self.intRow+1
        name = self.lineName.text()
        cur = self.conn.cursor()

        if self.tableType == "camino":  # Elección del tipo de tabla
            tipo = self.comboBoxTipo.currentText()
            if tipo == "Oficial":
                tp = 'o'
            elif tipo == "Anexo":
                tp = 'a'
            calidad = self.spinBoxCalidad.value()
            nivel = self.spinBoxNivel.value()
            km = self.spinBoxKm.value()
            tiempo = self.spinBoxTiempo.value()
            ref = self.lineRef.text()
            if self.radioBtnOn.isChecked():
                bici = True
            else:
                bici = False

            query = sql.SQL("INSERT INTO {table} (id, tipo, calidad, nivel, km, tiempo, bici) "
                            "VALUES (%s, %s, %s, %s, %s, %s, %s)").format(
                table=sql.Identifier(self.tableName))
            cur.execute(query, [id, tp, calidad, nivel, km, tiempo, bici])

            if ref:
                query = sql.SQL("UPDATE {table} SET ref=%s WHERE id=%s").format(
                    table=sql.Identifier(self.tableName))
                cur.execute(query, [ref, id])

        elif self.tableType == "punto":  # Elección del tipo de tabla
            zona = self.comboBoxZona.currentText()
            punto = self.spinBoxPunto.value()
            municipio = self.lineMunicipio.text()
            movilidad = self.lineMovilidad.text()
            if self.radioBtnOn.isChecked():
                aparcamiento = True
            else:
                aparcamiento = False

            query = sql.SQL("INSERT INTO {table} (id, zona, punto, aparcamiento) "
                            "VALUES (%s, %s, %s, %s)").format(
                table=sql.Identifier(self.tableName))
            cur.execute(query, [id, zona, punto, aparcamiento])

            if municipio:
                query = sql.SQL("UPDATE {table} SET municipio=%s WHERE id=%s").format(
                    table=sql.Identifier(self.tableName))
                cur.execute(query, [municipio, id])
            if movilidad:
                query = sql.SQL("UPDATE {table} SET movilidad=%s WHERE id=%s").format(
                    table=sql.Identifier(self.tableName))
                cur.execute(query, [movilidad, id])

        if name:
            query = sql.SQL("UPDATE {table} SET nombre=%s WHERE id=%s").format(
                table=sql.Identifier(self.tableName))
            cur.execute(query, [name, id])

        msgBox = QMessageBox()
        msgBox.setWindowTitle("Carga Satisfactoria")
        msgBox.setText("Se han cargado los datos")
        msgBox.setIcon(QMessageBox.Information)
        msgBox.exec()
        self.conn.commit()
        self.close()
