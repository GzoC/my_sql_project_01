
# 📊 Análisis de Datos con SQL en Python (SQLite)

## 🚀 Introducción

Este proyecto demuestra el uso de **SQL para análisis de datos** en **Python**, utilizando **SQLite** como base de datos relacional. Se trabaja con dos datasets (`orders.csv` y `products.csv`), los cuales se cargan en la base de datos `production.db`, permitiendo realizar consultas SQL para extraer información valiosa.

Este proyecto es parte de mi portafolio como **Data Analyst**, con el objetivo de fortalecer mis habilidades en **SQL, Python y bases de datos**.  

---

## 📂 **Estructura del Proyecto**

```
my_sql_project
│   README.md                 <- Documentación del proyecto
│   requirements.txt           <- Lista de dependencias necesarias
│
├── data                       <- Carpeta de datasets en formato CSV
│    ├── orders.csv            <- Datos de pedidos
│    ├── products.csv          <- Datos de productos
│
├── notebooks                  <- Carpeta con Jupyter Notebooks
│    ├── 01_sql_analysis.ipynb  <- Notebook principal con análisis SQL
│
└── db                         <- Carpeta de base de datos SQLite
     ├── production.db         <- Base de datos SQLite con datos cargados
```

---

## 🔧 **Requisitos y Configuración**

### 📌 **1. Clonar el repositorio**
Para descargar el proyecto, abre una terminal y ejecuta:

```bash
git clone https://github.com/tu_usuario/my_sql_project.git
cd my_sql_project
```

### 📌 **2. Crear un entorno virtual**
Recomendamos crear un entorno virtual para instalar las dependencias:

```bash
python -m venv sql_env
```

Activa el entorno:

- **Windows (CMD)**:
  ```bash
  sql_env\Scripts\activate
  ```
- **Windows (PowerShell)**:
  ```powershell
  sql_env\Scripts\Activate.ps1
  ```
- **Linux/Mac**:
  ```bash
  source sql_env/bin/activate
  ```

### 📌 **3. Instalar dependencias**
Ejecuta el siguiente comando para instalar las librerías necesarias:

```bash
pip install -r requirements.txt
```

### 📌 **4. Ejecutar el Notebook**
Inicia Jupyter Notebook con:

```bash
jupyter notebook
```

Abre el archivo `notebooks/01_sql_analysis.ipynb` y sigue las instrucciones.

---

## 🗂 **Descripción de los Datos**

### 📌 **1. Dataset `orders.csv`**
| order_id | product_id | quantity | order_date | status    |
|----------|-----------|----------|------------|-----------|
| 1        | 101       | 3        | 2023-01-10 | shipped   |
| 2        | 103       | 1        | 2023-01-11 | shipped   |
| 3        | 102       | 2        | 2023-01-12 | cancelled |
| 4        | 101       | 5        | 2023-01-15 | shipped   |
| 5        | 104       | 2        | 2023-01-15 | pending   |
| 6        | 105       | 7        | 2023-01-18 | shipped   |

**Descripción de columnas:**
- `order_id`: Identificador único del pedido.
- `product_id`: ID del producto comprado.
- `quantity`: Cantidad de productos en el pedido.
- `order_date`: Fecha en la que se realizó el pedido.
- `status`: Estado del pedido (`shipped`, `cancelled`, `pending`).

### 📌 **2. Dataset `products.csv`**
| product_id | product_name  | price  | category   |
|------------|--------------|--------|------------|
| 101        | Widget A      | 25.50  | Category A |
| 102        | Widget B      | 15.00  | Category A |
| 103        | Thingamajig   | 40.75  | Category B |
| 104        | Gadget        | 10.00  | Category A |
| 105        | Machine Part  | 50.00  | Category C |

**Descripción de columnas:**
- `product_id`: Identificador único del producto.
- `product_name`: Nombre del producto.
- `price`: Precio unitario del producto.
- `category`: Categoría a la que pertenece.

---

## 📊 **Consultas SQL Implementadas**
✅ `SELECT * FROM orders;` → Consulta todos los pedidos.  
✅ `SELECT * FROM products;` → Consulta todos los productos.  
✅ `SELECT * FROM orders WHERE status = 'shipped';` → Filtra pedidos enviados.  
✅ `SELECT * FROM products ORDER BY price DESC;` → Ordena productos por precio.  
✅ `SELECT product_id, COUNT(*) FROM orders GROUP BY product_id;` → Agrupa pedidos por producto.  
✅ `SELECT o.order_id, p.product_name, o.quantity FROM orders o JOIN products p ON o.product_id = p.product_id;` → JOIN entre `orders` y `products`.  
✅ `SELECT * FROM orders WHERE product_id IN (SELECT product_id FROM products WHERE category = 'Category A');` → Subconsulta de productos en `Category A`.  

🔹 **Ver más consultas en el Notebook** `notebooks/01_sql_analysis.ipynb`.

---

## 🚀 **Objetivos del Proyecto**
✅ Aplicar **SQL** para el análisis de datos.  
✅ Usar **SQLite** para gestionar bases de datos relacionales.  
✅ Integrar **Python + SQL** en un flujo de trabajo de Data Analytics.  
✅ Construir un proyecto **real y profesional** para el portafolio.  
✅ Demostrar habilidades en **Git, GitHub y control de versiones**.  

---

## 🤝 **Contribuciones**
¡Todas las contribuciones son bienvenidas! Para colaborar:
1. **Haz un fork** del repositorio.
2. **Crea una nueva rama**:  
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
3. **Realiza cambios y haz commit**:  
   ```bash
   git commit -m "Añadida nueva consulta SQL"
   ```
4. **Envía tu contribución con un Pull Request**.

---

## 📜 **Licencia**
Este proyecto está bajo la licencia **MIT**, lo que significa que puedes utilizarlo y modificarlo libremente, pero sin garantías. Revisa el archivo `LICENSE` para más detalles.

---

## 📞 **Contacto**
📧 **Email:** [cisternasalinasg@gmail.com]
🔗 **LinkedIn:** [linkedin.com/in/gonzalo-cisterna-salinas-369203119] 
🌐 **Portafolio:** [https://github.com/GzoC]

---

💡 **Si este proyecto te resultó útil, dale una ⭐ en GitHub y sígueme para más proyectos de Data Analytics. 🚀**  
```

