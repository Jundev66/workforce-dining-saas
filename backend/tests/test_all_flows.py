import asyncio
import json
from src.contexts.copilot.application.copilot_graph import CopilotWorkflow

async def main():
    workflow = CopilotWorkflow()

    scenarios = [
        {
            "name": "Escenario 1: Ausencia Médica + Cancelación de Vianda",
            "msg": "El viernes no asisto por consulta médica y por favor cancelar mi vianda de almuerzo",
        },
        {
            "name": "Escenario 2: Ausencia Personal (Sin cancelar vianda)",
            "msg": "El lunes falto a mi turno por trámites personales urgentes",
        },
        {
            "name": "Escenario 3: Consulta General",
            "msg": "¿Cómo funciona la política de licencias y comedor de la empresa?",
        },
    ]

    for sc in scenarios:
        print(f"\n=======================================================")
        print(f"PROBANDO: {sc['name']}")
        print(f"Mensaje: \"{sc['msg']}\"")
        print(f"=======================================================")

        res = await workflow.run(
            tenant_id="tenant-prod-001",
            employee_id="emp-juan-perez",
            message=sc["msg"],
        )

        print(f"-> Intención detectada: {res['intent']['intent']}")
        print(f"-> Requiere cancelar vianda: {res['intent']['cancel_meal']}")
        print(f"-> Veredicto Política RRHH: {res['policy_verdict']['policy_code']} (Aprobado={res['policy_verdict']['approved']})")
        if res.get("dining_action"):
            print(f"-> Acción Comedor: Código={res['dining_action']['confirmation_code']}, Ahorro={res['dining_action']['saved_portion_kg']} kg")
        else:
            print(f"-> Acción Comedor: No requerida (Omitida por arista condicional)")
        print(f"-> Guardrail Invariantes: {'PASÓ' if res['guardrail_passed'] else 'FALLÓ'}")
        print(f"-> Respuesta Final al Usuario:\n   \"{res['final_response']}\"")
        print(f"-> Trazabilidad Multi-Agente (Audit Trail):")
        for step in res["audit_trail"]:
            print(f"   * {step}")

if __name__ == "__main__":
    asyncio.run(main())
