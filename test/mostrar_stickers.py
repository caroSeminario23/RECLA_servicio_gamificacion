import unittest
import requests
import concurrent.futures
import time
import random

class TestStickersCarga(unittest.TestCase):
    """
    Pruebas de carga para el servicio de obtener stickers con estado
    """
    
    BASE_URL = "http://localhost:5001/sticker_routes"  
    ENDPOINT_STICKERS = f"{BASE_URL}/get_stickers_con_estado"
    
    # IDs de usuarios de prueba (ajusta según tu BD)
    USUARIOS_PRUEBA = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
    
    # Categorías de stickers disponibles (ajusta según tu BD)
    CATEGORIAS_STICKERS = [1, 2, 3]
    
    @staticmethod
    def generar_payload_aleatorio(numero_usuario):
        """Genera un payload aleatorio para consultar stickers"""
        id_usuario = TestStickersCarga.USUARIOS_PRUEBA[numero_usuario % len(TestStickersCarga.USUARIOS_PRUEBA)]
        categoria = random.choice(TestStickersCarga.CATEGORIAS_STICKERS)
        
        return {
            "id_usuario": id_usuario,
            "categoria": categoria
        }
    
    @staticmethod
    def consultar_stickers_individual(url, payload, numero_intento):
        """Consulta stickers de forma individual y retorna el resultado"""
        try:
            inicio = time.time()
            respuesta = requests.post(url, json=payload, timeout=10)
            tiempo_respuesta = time.time() - inicio
            
            return {
                "intento": numero_intento,
                "status_code": respuesta.status_code,
                "tiempo_respuesta": tiempo_respuesta,
                "respuesta": respuesta.json(),
                "exito": respuesta.status_code == 200,
                "error": None,
                "id_usuario": payload["id_usuario"],
                "categoria": payload["categoria"]
            }
        except Exception as e:
            tiempo_respuesta = time.time() - inicio
            return {
                "intento": numero_intento,
                "status_code": None,
                "tiempo_respuesta": tiempo_respuesta,
                "respuesta": None,
                "exito": False,
                "error": str(e),
                "id_usuario": payload["id_usuario"],
                "categoria": payload["categoria"]
            }
    
    def simular_consultas_simultaneas(self, cantidad_usuarios):
        """
        Simula consultas simultáneas al servicio de stickers
        
        Args:
            cantidad_usuarios (int): Cantidad de consultas simultáneas (1-20)
        
        Returns:
            dict: Estadísticas del test de carga
        """
        
        if not (1 <= cantidad_usuarios <= 20):
            raise ValueError("La cantidad de usuarios debe estar entre 1 y 20")
        
        print(f"\n{'='*80}")
        print(f"INICIANDO TEST DE CARGA: {cantidad_usuarios} consultas simultáneas")
        print(f"Endpoint: {self.ENDPOINT_STICKERS}")
        print(f"{'='*80}\n")
        
        # Generar payloads para las consultas
        payloads = [self.generar_payload_aleatorio(i) for i in range(cantidad_usuarios)]
        
        # Ejecutar consultas en paralelo
        tiempo_inicio_total = time.time()
        resultados = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=cantidad_usuarios) as executor:
            futures = [
                executor.submit(
                    self.consultar_stickers_individual,
                    self.ENDPOINT_STICKERS,
                    payloads[i],
                    i + 1
                )
                for i in range(cantidad_usuarios)
            ]
            
            for future in concurrent.futures.as_completed(futures):
                resultados.append(future.result())
        
        tiempo_total = time.time() - tiempo_inicio_total
        
        # Procesar estadísticas
        exitosos = sum(1 for r in resultados if r["exito"])
        fallidos = cantidad_usuarios - exitosos
        tiempo_promedio = sum(r["tiempo_respuesta"] for r in resultados) / cantidad_usuarios
        tiempo_maximo = max(r["tiempo_respuesta"] for r in resultados)
        tiempo_minimo = min(r["tiempo_respuesta"] for r in resultados)
        
        # Mostrar resultados
        self._mostrar_resultados(
            cantidad_usuarios, exitosos, fallidos, 
            tiempo_total, tiempo_promedio, tiempo_maximo, 
            tiempo_minimo, resultados
        )
        
        return {
            "cantidad_usuarios": cantidad_usuarios,
            "exitosos": exitosos,
            "fallidos": fallidos,
            "tiempo_total": tiempo_total,
            "tiempo_promedio": tiempo_promedio,
            "tiempo_maximo": tiempo_maximo,
            "tiempo_minimo": tiempo_minimo,
            "resultados_detallados": resultados
        }
    
    @staticmethod
    def _mostrar_resultados(cantidad, exitosos, fallidos, tiempo_total, 
                            tiempo_promedio, tiempo_maximo, tiempo_minimo, resultados):
        """Muestra los resultados en formato legible"""
        print(f"RESUMEN DE RESULTADOS:")
        print(f"-" * 80)
        print(f"Total de consultas:           {cantidad}")
        print(f"Consultas exitosas:           {exitosos} ✓")
        print(f"Consultas fallidas:           {fallidos} ✗")
        print(f"Tasa de éxito:                {(exitosos/cantidad)*100:.1f}%")
        print(f"\nTIEMPOS DE RESPUESTA:")
        print(f"-" * 80)
        print(f"Tiempo total:                 {tiempo_total:.3f}s")
        print(f"Tiempo promedio/consulta:     {tiempo_promedio:.3f}s")
        print(f"Tiempo máximo:                {tiempo_maximo:.3f}s")
        print(f"Tiempo mínimo:                {tiempo_minimo:.3f}s")
        print(f"\nDETALLES POR CONSULTA:")
        print(f"-" * 80)
        
        for resultado in sorted(resultados, key=lambda x: x["intento"]):
            estado = "✓" if resultado["exito"] else "✗"
            print(f"Consulta {resultado['intento']:2d}: {estado} | "
                  f"Status: {resultado['status_code'] or 'ERROR':>3} | "
                  f"Usuario: {resultado['id_usuario']:>2} | "
                  f"Categoría: {resultado['categoria']} | "
                  f"Tiempo: {resultado['tiempo_respuesta']:.3f}s", end="")
            if resultado["error"]:
                print(f" | Error: {resultado['error']}")
            else:
                print()
        
        print(f"{'='*80}\n")
    
    def test_1_usuario(self):
        """Test con 1 consulta simultánea"""
        resultado = self.simular_consultas_simultaneas(1)
        self.assertEqual(resultado["exitosos"], 1)
    
    def test_5_usuarios(self):
        """Test con 5 consultas simultáneas"""
        resultado = self.simular_consultas_simultaneas(5)
        self.assertGreaterEqual(resultado["exitosos"], 4)
    
    def test_10_usuarios(self):
        """Test con 10 consultas simultáneas"""
        resultado = self.simular_consultas_simultaneas(10)
        self.assertGreaterEqual(resultado["exitosos"], 8)

    def test_15_usuarios(self):
        """Test con 15 consultas simultáneas"""
        resultado = self.simular_consultas_simultaneas(15)
        self.assertGreaterEqual(resultado["exitosos"], 12)
    
    def test_20_usuarios(self):
        """Test con 20 consultas simultáneas (máximo)"""
        resultado = self.simular_consultas_simultaneas(20)
        self.assertGreaterEqual(resultado["exitosos"], 15)


if __name__ == "__main__":
    # Ejecutar pruebas
    unittest.main(verbosity=2)
    
    # O ejecutar directamente sin unittest:
    # test = TestStickersCarga()
    # test.simular_consultas_simultaneas(10)