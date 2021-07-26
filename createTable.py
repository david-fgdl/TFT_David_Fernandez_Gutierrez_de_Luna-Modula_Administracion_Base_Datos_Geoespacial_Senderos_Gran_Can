from PyQt5.Qt import *
from psycopg2 import sql

class createTableWindow(QWidget):
    def __init__(self, connection, parent=None):
        super(createTableWindow, self).__init__(parent)
        self.conn = connection

        layout = QFormLayout()

        self.nameButton = QPushButton("Introducir nombre")
        self.nameButton.clicked.connect(self.getName)
        self.nameLine = QLineEdit()
        layout.addRow(self.nameButton, self.nameLine)

        self.optionButton = QPushButton("Escojer tipo de tabla")
        self.optionButton.clicked.connect(self.getItem)
        self.tableLine = QLineEdit()
        layout.addRow(self.optionButton, self.tableLine)

        self.okButton = QPushButton("OK")
        self.okButton.clicked.connect(self.createTable)
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.close)
        layout.addRow(self.okButton, self.cancelButton)

        self.setLayout(layout)
        self.setWindowTitle("Seleccion tipo de Tabla")
        self.resize(300, 50)

    """
        Función para introducir el tipo de tabla
    """
    def getItem(self):
        items = ("Camino", "Punto de Red")
        item, ok = QInputDialog.getItem(self, "Selección de tabla", "Lista de tablas", items, 0, False)
        if ok and item:
            self.tableLine.setText(item)

    """
        Función para introducir el nombre en la ventana de crear tabla
    """
    def getName(self):
        text, ok = QInputDialog.getText(self, 'Nombre de Tabla', 'Introduzca nombre de tabla:')
        if ok:
            self.nameLine.setText(str(text))

    """
        Función que crea la nueva tabla
    """
    def createTable(self):
        if self.nameLine.text() == "":
            self.message("Error", "Nombre no válido", 1)
            return
        cur = self.conn.cursor()
        if self.tableLine.text() == "Camino":
            query = sql.SQL("""
            CREATE TABLE {table}(
                id integer NOT NULL,
                geom geometry(MultiLineStringZ,4326),
                nombre character varying COLLATE pg_catalog."default",
                tipo character(1) COLLATE pg_catalog."default",
                calidad integer,
                nivel integer,
                km integer,
                tiempo integer,
                ref character varying COLLATE pg_catalog."default",
                bici boolean,
                principio integer,
                final integer,
                CONSTRAINT {constraint} PRIMARY KEY (id)
            )""").format(
                table=sql.Identifier(self.nameLine.text()),
                constraint=sql.Identifier(self.nameLine.text() + "_pkey"))
        elif self.tableLine.text() == "Punto de Red":
            query = sql.SQL("""
            CREATE TABLE {table}(
            id integer NOT NULL,
            geom geometry(PointZ,4326),
            name character varying COLLATE pg_catalog."default",
            zona character varying COLLATE pg_catalog."default",
            punto integer,
            municipio character varying COLLATE pg_catalog."default",
            movilidad character varying COLLATE pg_catalog."default",
            aparcamiento boolean,
            CONSTRAINT {constraint} PRIMARY KEY (id)
                )""").format(
                table=sql.Identifier(self.nameLine.text()),
                constraint=sql.Identifier(self.nameLine.text() + "_pkey"))
        else:
            self.message("Error", "Tabla no valida", 1)
            return

        cur.execute(query)
        self.conn.commit()
        self.tableLine.setText("")
        self.nameLine.setText("")
        self.message("Mensaje de confirmación", "Tabla Creada", 0)
        self.close()

    def message(self, title, text, opt):
        msgBox = QMessageBox()
        msgBox.setWindowTitle(title)
        msgBox.setText(text)
        if opt == 0:
            msgBox.setIcon(QMessageBox.Information)
        else:
            msgBox.setIcon(QMessageBox.Critical)
        msgBox.exec()
