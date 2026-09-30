import os
import django
import random
from pathlib import Path

# Configuración del entorno de Django
BASE_DIR = Path(__file__).resolve().parent
settings_folder = next(p.parent.name for p in BASE_DIR.glob('**/settings.py'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'{settings_folder}.settings')
django.setup()

from store.models import Categoria, Producto

# Estructura de Categorías, Códigos Iniciales, Marcas y Tipos de Productos
DATOS_CATEGORIAS = {
    'LACTEOS': {
        'codigo_base': 10000,
        'marcas': ['Foremost', 'Dos Pinos', 'Lala', 'Trebolac', 'Parma', 'Bregi'],
        'productos': [
            'Leche Entera 1L', 'Leche Descremada 1L', 'Leche Semidescremada 1L', 'Leche Deslactosada 1L',
            'Queso Fresco 400g', 'Queso Muzzarella 200g', 'Queso Americano 12 Lascas', 'Queso Crema 200g',
            'Crema Pura 400ml', 'Yogurt Fresa 1L', 'Yogurt Melocotón 1L', 'Yogurt Natural 500g',
            'Mantequilla con Sal 200g', 'Mantequilla sin Sal 200g', 'Leche Condensada 397g'
        ]
    },
    'EMBUTIDOS': {
        'codigo_base': 20000,
        'marcas': ['Perry', 'Toledo', 'Deli Premium', 'Frito Lay', 'Zwan', 'San Rafael'],
        'productos': [
            'Jamón de Pavo 250g', 'Jamón Virginia 250g', 'Salchicha Fud 500g', 'Salchicha de Pavo 500g',
            'Chorizo Rojo 1lb', 'Chorizo Negro 1lb', 'Longaniza Tradicional 1lb', 'Tocino Ahumado 250g',
            'Salami Italiano 200g', 'Mortadela Especial 250g', 'Jamón Horneado 250g', 'Salchichón Premium 400g'
        ]
    },
    'CARNES': {
        'codigo_base': 30000,
        'marcas': ['Pollo Rey', 'Pio Lindo', 'Corte Real', 'El Arreo', 'Delicarnes'],
        'productos': [
            'Pollo Entero con Menudos 1lb', 'Pechuga de Pollo Deshuesada 1lb', 'Muslo de Pollo 1lb',
            'Carne Molida de Res Especial 1lb', 'Lomo de Res 1lb', 'Puyaso de Res 1lb', 'Bistec de Res 1lb',
            'Chuleta de Cerdo Ahumada 1lb', 'Lomo de Cerdo 1lb', 'Costilla de Cerdo 1lb', 'Carne para Asar 1lb'
        ]
    },
    'GASEOSAS Y BEBIDAS': {
        'codigo_base': 40000,
        'marcas': ['Coca-Cola', 'Pepsi', 'Mirinda', '7UP', 'Gatorade', 'Petit', 'Kern\'s', 'SalvaVida', 'Monster'],
        'productos': [
            'Gaseosa 3L', 'Gaseosa 2L', 'Gaseosa 1.5L', 'Gaseosa Lata 355ml', 'Gaseosa Vidrio 12oz',
            'Jugo de Naranja 1L', 'Jugo de Durazno 1L', 'Jugo de Manzana 1L', 'Bebida Energizante 473ml',
            'Agua Pura 600ml', 'Agua Pura 5L', 'Agua Con Gas 600ml', 'Isotónico Frutas Tropicales 600ml'
        ]
    },
    'GRANOS Y ABARROTES': {
        'codigo_base': 50000,
        'marcas': ['Ina', 'B&B', 'Doña Blanca', 'Verde Campo', 'Maggi', 'Natura\'s', 'Ideal'],
        'productos': [
            'Arroz Blanco 1lb', 'Arroz Precocido 1lb', 'Frijol Negro 1lb', 'Frijol Rojo 1lb',
            'Azúcar Caña 1lb', 'Aceite Vegetal 800ml', 'Aceite de Oliva 500ml', 'Pasta Espagueti 200g',
            'Pasta Codo 200g', 'Salsa de Tomate Dulce 200g', 'Sazón Completo 100g', 'Consomé de Pollo 12 sobres'
        ]
    },
    'SNACKS Y REPOSTERIA': {
        'codigo_base': 60000,
        'marcas': ['Lays', 'Doritos', 'Tortrix', 'Ruffles', 'Pozuelo', 'Gama', 'Bimbo', 'Marinela'],
        'productos': [
            'Tortrix Limón 150g', 'Doritos Queso 180g', 'Papas Lays Sal 160g', 'Plataninas 200g',
            'Galletas Chiky 60g', 'Galletas Club Extra 200g', 'Pan Molde Blanco', 'Pan Molde Integral',
            'Magdalena Vainilla', 'Donas de Chocolate 4 unidades', 'Chocolates Surtidos 100g'
        ]
    },
    'LIMPIEZA DEL HOGAR': {
        'codigo_base': 70000,
        'marcas': ['Xedex', 'Rinso', 'Axion', 'Clorox', 'Suavitel', 'Lysol', 'Fabuloso'],
        'productos': [
            'Detergente en Polvo 1kg', 'Detergente Líquido 2L', 'Jabón Lavaplatos Crema 425g',
            'Cloro Regular 1L', 'Desinfectante Lavanda 1L', 'Suavizante de Telas 850ml',
            'Limpiavidrios 500ml', 'Esponja Multiuso 3 pack', 'Bolsas para Basura 10 unidades'
        ]
    },
    'LICORES Y CERVEZAS': {
        'codigo_base': 80000,
        'marcas': ['Gallo', 'Brahva', 'Modelo', 'Botran', 'Venado', 'Johnny Walker', 'Smirnoff'],
        'productos': [
            'Cerveza Draft 350ml', 'Cerveza Lata 12oz', 'Cerveza Botella 330ml', 'Six Pack Cerveza',
            'Ron Botran Añejo 750ml', 'Aguardiente Venado 750ml', 'Whisky Red Label 750ml', 'Vodka 750ml'
        ]
    }
}

def generar_datos():
    print("Iniciando la carga masiva de productos...")
    
    total_creados = 0
    
    for nombre_cat, datos in DATOS_CATEGORIAS.items():
        # Crear o consultar la categoría
        categoria_obj, created = Categoria.objects.get_or_create(
            nombre=nombre_cat,
            defaults={'descripcion': f'Categoría general de {nombre_cat.lower()}'}
        )
        
        codigo_actual = datos['codigo_base']
        
        # Generar 50 productos variados por categoría
        for i in range(1, 51):
            # Asegurar un código de barras incremental (ej. 20000, 20001, 20002...)
            codigo_barras = str(codigo_actual)
            
            # Seleccionar marca y tipo
            marca = random.choice(datos['marcas'])
            producto_base = random.choice(datos['productos'])
            
            # Para evitar nombres duplicados exactos en la generación de 50 ítems
            variacion = f"Var. {i}" if i > len(datos['productos']) else ""
            nombre_producto = f"{producto_base} {marca} {variacion}".strip()
            
            precio = round(random.uniform(5.00, 150.00), 2)
            stock = random.randint(10, 100)
            
            # Crear producto en la base de datos PostgreSQL
            Producto.objects.get_or_create(
                codigo_barras=codigo_barras,
                defaults={
                    'nombre': nombre_producto,
                    'descripcion': f'{nombre_producto} - Presentación de alta calidad.',
                    'precio': precio,
                    'stock': stock,
                    'categoria': categoria_obj,
                    'activo': True
                }
            )
            
            codigo_actual += 1
            total_creados += 1

    print(f"¡Proceso completado con éxito! Se poblaron {total_creados} productos en {len(DATOS_CATEGORIAS)} categorías.")

if __name__ == '__main__':
    generar_datos()