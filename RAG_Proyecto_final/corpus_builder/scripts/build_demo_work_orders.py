"""Build 100 clearly synthetic, manual-bounded demonstration work orders."""
import csv
from datetime import date, timedelta
from pathlib import Path

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "corpus_builder/input/equipment_catalog.csv"
OUTPUT = ROOT / "corpus_builder/input/work_orders_master.xlsx"
TECHNICIANS = ["Laura Méndez", "Diego Salas", "Mariana Torres", "Carlos Vega", "Ana Ruiz"]

# Each scenario records observations that can be checked against the listed
# source. The generator never turns these examples into manufacturer claims.
SCENARIOS = {
    "PRN-HP-01": [
        ("Atasco de papel durante alimentación desde bandeja", "El atasco se localizó en la ruta indicada por el panel; se registró la bandeja y el soporte usados.", "Restos de papel o condición de alimentación por confirmar.", "Se documentó la ubicación, se retiró el papel accesible siguiendo la guía del usuario y se hizo una prueba controlada.", "No aplica", "Registrar bandeja, soporte y ubicación del atasco; escalar si se repite."),
        ("Impresión con densidad o contraste irregular", "La página de prueba mostró variación visible; se revisaron ajustes y estado de consumibles según la guía.", "Ajuste de impresión o consumible pendiente de verificación.", "Se guardó una muestra, se revisaron ajustes disponibles y se repitió una página de prueba.", "No aplica", "Conservar muestra y ajustes; solicitar servicio si persiste."),
        ("El equipo solicita atención relacionada con tóner o consumible", "El mensaje y el consumible instalado se registraron; no se identificó un código de error del fabricante.", "Consumible agotado, no reconocido o instalado de forma incorrecta por confirmar.", "Se verificó el mensaje en la guía del usuario y se comprobó la instalación sin abrir conjuntos internos.", "Consumible sujeto a inspección", "Registrar texto exacto del panel y referencia compatible; no reutilizar piezas dañadas."),
        ("Repetición de atasco al imprimir un lote", "El patrón se reprodujo con una bandeja y soporte concretos; se anotaron páginas y condiciones.", "Condición de papel o componente de alimentación por diagnosticar.", "Se comparó el soporte con las recomendaciones del fabricante y se documentó la ubicación indicada por el equipo.", "No aplica", "Si se repite, remitir las observaciones al servicio técnico autorizado."),
        ("Revisión preventiva de calidad y estado del equipo", "La lista de comprobación se completó y se archivaron páginas de prueba y mensajes presentes.", "No se confirmó avería; revisión limitada a las comprobaciones descritas en la guía.", "Se revisaron indicaciones visibles del usuario, consumibles y calidad de impresión; cualquier servicio interno quedó escalado.", "No aplica", "Mantener registro por fecha, consumible y síntoma; seguir el manual de servicio para reparaciones."),
    ],
    "CUT-IDEAL-01": [
        ("La barrera de luz infrarroja indica una condición de seguridad", "La indicación se observó sin intentar activar el corte ni puentear el dispositivo.", "Obstrucción o condición de seguridad pendiente de evaluar por personal autorizado.", "Se detuvo el uso, se registró la indicación y se solicitó revisión conforme al manual oficial de operación.", "No aplica", "No puentear resguardos; mantener fuera de servicio hasta verificar la condición segura."),
        ("El valor mostrado para el tope trasero no coincide con la muestra", "Se registraron el valor de pantalla, el ajuste elegido y la medición de una muestra sin ejecutar ajustes internos.", "Referencia, programa o medición por comprobar.", "Se cotejó la selección del programa y se guardó la lectura; cualquier calibración se escaló al servicio autorizado.", "No aplica", "Verificar programa y unidades antes del lote; documentar muestra y lectura."),
        ("La pantalla táctil no conserva el programa de trabajo esperado", "Se anotó el número de programa y los pasos observados; el folleto identifica operación programable.", "Selección o configuración del programa por confirmar.", "Se documentó la configuración visible y se pidió validación al operador; no se alteraron parámetros de seguridad.", "No aplica", "Validar el programa con una prueba segura y consultar instrucciones completas del fabricante."),
        ("La lectura del manómetro de presión de sujeción parece distinta a la referencia del turno", "Se registró la lectura visible sin intervenir en el circuito hidráulico.", "Variación por confirmar; el folleto describe un manómetro y ajuste de presión.", "Se detuvo el lote y se solicitó inspección por técnico cualificado conforme al manual oficial.", "No aplica", "No ajustar el sistema hidráulico sin el procedimiento oficial y personal autorizado."),
        ("Inspección de condiciones visibles antes de producción", "La inspección se limitó a elementos visibles descritos en el folleto: cortina, cubierta y controles de operación a dos manos.", "No se confirma fallo mecánico; el documento local es un folleto, no una guía de mantenimiento.", "Se registraron las condiciones visibles y se retiró de servicio cualquier elemento de seguridad dudoso.", "No aplica", "Obtener y seguir el manual oficial completo para operación y mantenimiento."),
    ],
    "PC-HP-01": [
        ("La estación muestra aviso durante el diagnóstico de almacenamiento", "Se guardó el mensaje y el resultado del diagnóstico sin retirar componentes.", "Unidad o conexión por diagnosticar según el manual de servicio aplicable.", "Se respaldaron datos disponibles y se escaló el diagnóstico al proveedor autorizado.", "No aplica", "No sustituir piezas hasta confirmar generación exacta y procedimiento de servicio."),
        ("Apagado inesperado durante una carga de trabajo", "Se registraron hora, alimentación, temperatura ambiental y mensajes observados.", "Causa no determinada; requiere diagnóstico del modelo y configuración exactos.", "Se ejecutaron solo comprobaciones externas y diagnósticos indicados por el usuario; se preservaron registros.", "No aplica", "Solicitar evaluación técnica si el evento se repite; no abrir el equipo sin autorización."),
        ("La batería reporta menor autonomía que la esperada", "Se anotó el estado indicado por el sistema y el comportamiento con alimentación conectada.", "Desgaste de batería u otra causa por confirmar mediante diagnóstico.", "Se respaldó el estado de diagnóstico y se comprobó el adaptador externamente.", "Batería pendiente de evaluación", "Confirmar el submodelo y compatibilidad antes de reemplazar componentes."),
        ("El ventilador genera ruido o la temperatura parece elevada", "Se registró el contexto de carga y los avisos; no se abrió el chasis.", "Flujo de aire o componente térmico requiere evaluación profesional.", "Se detuvo la carga, se revisaron externamente las entradas de aire y se solicitó servicio autorizado.", "No aplica", "No operar si aparecen avisos térmicos; seguir las advertencias de seguridad del manual."),
        ("Inspección preventiva de datos de diagnóstico", "Se comprobó el estado visible del sistema y se guardó el resultado de los diagnósticos disponibles.", "Sin avería confirmada; el manual de servicio limita algunos procedimientos a proveedores autorizados.", "Se verificó respaldo, registros de diagnóstico y condición externa; no se desmontó el equipo.", "No aplica", "Anotar número de producto y generación; usar el manual exacto antes de cualquier reparación."),
    ],
    "PRN-KODAK-01": [
        ("Un trabajo enviado no aparece en la cola esperada", "Se registraron identificador del trabajo, cola y respuesta observada de la interfaz.", "Destino o estado del trabajo por comprobar; la referencia local cubre interfaces de software.", "Se verificaron los parámetros de envío y estado de cola documentados; no se intervino el motor de impresión.", "No aplica", "Adjuntar el registro de interfaz y consultar soporte del modelo antes de cambios de producción."),
        ("Los atributos del trabajo no coinciden con la solicitud", "Se compararon atributos enviados y valores devueltos por la interfaz documentada.", "Mapeo de atributos o configuración del flujo por revisar.", "Se guardó una copia de la solicitud y se corrigió el perfil de envío bajo control del operador.", "No aplica", "Validar una prueba antes de liberar un lote; la fuente local no prescribe reparación mecánica."),
        ("La respuesta del sistema informa rechazo de un comando de cola", "Se guardó la respuesta literal y la secuencia de comandos pertinente.", "Comando, estado o permiso de interfaz no compatible con la sesión.", "Se revisó la secuencia contra la referencia técnica y se escaló el caso al administrador del flujo.", "No aplica", "No inventar códigos de error; conservar la respuesta original para soporte."),
        ("La selección de medio o destino difiere entre trabajos", "Se compararon los valores de medio y destino definidos por la interfaz.", "Parámetros de trabajo o configuración del sistema por confirmar.", "Se documentaron los valores y se corrigió la plantilla de envío con autorización del responsable.", "No aplica", "Probar con un trabajo controlado y conservar la plantilla aprobada."),
        ("Revisión preventiva de integración de trabajos", "Se comprobaron estados de cola, atributos y respuestas de prueba de la interfaz.", "No se confirmó una avería física; las fuentes locales son especificaciones de interfaz.", "Se archivaron resultados de prueba y cambios de configuración; cualquier fallo de prensa se derivó a soporte Kodak.", "No aplica", "Para mantenimiento físico, obtener el manual de servicio oficial del modelo exacto."),
    ],
}


def main() -> None:
    with CATALOG.open(encoding="utf-8-sig", newline="") as stream:
        catalog = {row["equipment_id"]: row for row in csv.DictReader(stream)}
    headers = ["work_order_id", "equipment_id", "manufacturer", "model", "equipment_type",
               "opened_at", "closed_at", "maintenance_type", "reported_symptom", "error_code",
               "diagnosis", "root_cause", "actions_performed", "parts_used", "technician",
               "downtime_hours", "status", "recommendations", "notes"]
    wb = Workbook()
    ws = wb.active
    ws.title = "work_orders"
    ws.append(headers)
    order_number = 0
    start = date(2025, 1, 6)
    for equipment_id, scenarios in SCENARIOS.items():
        equipment = catalog[equipment_id]
        for scenario_index, scenario in enumerate(scenarios):
            symptom, diagnosis, cause, actions, parts, recommendation = scenario
            for variant in range(5):
                order_number += 1
                day_offset = (order_number - 1) * 6
                opened = start + timedelta(days=day_offset)
                closed = opened + timedelta(days=(order_number + variant) % 3)
                maintenance = ("preventive", "corrective", "inspection", "corrective", "preventive")[variant]
                ws.append([f"OT-{order_number:04d}", equipment_id, equipment["manufacturer"],
                           equipment["model"], equipment["equipment_type"], opened, closed,
                           maintenance, f"{symptom}. Caso de demostración {variant + 1}.", "",
                           diagnosis, cause, actions, parts, TECHNICIANS[(order_number - 1) % len(TECHNICIANS)],
                           round(0.5 + ((order_number * 7) % 30) / 10, 1), "closed", recommendation,
                           (f"Orden sintética de demostración; escenario {scenario_index + 1}, variante {variant + 1}. "
                            "No representa una intervención real ni certifica un procedimiento del fabricante. "
                            "Verificar manual oficial y modelo exacto antes de cualquier intervención.")])
    wb.save(OUTPUT)
    print(f"Generadas {order_number} filas sintéticas en {OUTPUT}")


if __name__ == "__main__":
    main()
