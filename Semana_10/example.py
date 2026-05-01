from logic import And, Not, Implication, Or, Symbol, Biconditional, model_check

# Symbols
# "Rain"
# "Hagrid"
# "Dumbledore"

rain = Symbol("Rain")
hagrid = Symbol("Hagrid")
dumbledore = Symbol("Dumbledore")

# knowledge
knowledge = And()


# Si no llovió, Harry visitó a Hagrid hoy
knowledge.add(
    Implication(Not(rain), hagrid)
)

# Harry visitó a Hagrid o a Dumbledore hoy, pero no a ambos
knowledge.add(
    And( 
        Or(hagrid, dumbledore),
        Not(
            And(hagrid, dumbledore)
        )
    )
)

# Harry visitó a Dumbledore hoy
knowledge.add(dumbledore)


print(f"Rain: {model_check(knowledge, rain)}")
print(f"Hagrid: {model_check(knowledge, hagrid)}")
print(f"Dumbledore: {model_check(knowledge, dumbledore)}")




# 1. Si estudio o hago tareas, entonces paso el curso, pero si no estudio, no paso.

estudio = Symbol("Estudio")
tareas = Symbol("Tareas")
paso = Symbol("paso")

knowledge = And()


# si estudio o hago tareas, entonces paso el curso
knowledge.add(
    Implication(
        Or(estudio, tareas), 
        paso
    )
)

# si no estudio, no paso
knowledge.add(
    Implication(
        Not(estudio), 
        Not(paso)
    )
)

# estudio
knowledge.add(estudio)


print(f"\n1.")
print(f"Paso el curso: {model_check(knowledge, paso)}")
print(f"No paso el curso: {model_check(knowledge, Not(paso))}")



# 2. si estudio, entonces si hago tareas paso el curso
knowledge = And()


knowledge.add(
    And(estudio,
        Implication(tareas, paso)    
    )
)

knowledge.add(estudio)
knowledge.add(tareas)

print(f"\n2.")
print(f"Paso el curso: {model_check(knowledge, paso)}")




# 3. Voy al cine si y solo si termino la tarea y no estoy cansado
cine = Symbol("Cine")
cansado = Symbol("Cansado")


knowledge.add(
    Biconditional(
        cine,
        And(
            tareas,
            Not(cansado)
        )
    )
)

knowledge.add(tareas)
knowledge.add(Not(cansado))

print(f"\n3.")
print(f"Voy al cine: {model_check(knowledge, cine)}")
print(f"No voy al cine: {model_check(knowledge, Not(cine))}")


# 4. Si el sistema responde y no hay timeout, entonces la transacción 
# se procesa; de lo contrario, falla.

sistema = Symbol("Sistema")
timeout = Symbol("Timeout")
procesada = Symbol("Procesada")
falla = Symbol("Falla")

knowledge = And()

knowledge.add(
    Implication(
        And(sistema,
            Not(timeout)
        ),
        procesada
    )
)

knowledge.add(sistema)
knowledge.add(Not(timeout))

print(f"\n4.")
print(f"La transacción se procesa: {model_check(knowledge, procesada)}")
print(f"La transacción falla: {model_check(knowledge, Not(procesada))}")




# 5. No es cierto que si estudio entonces paso.

knowledge = And()

knowledge.add(Not(Implication(estudio, paso)))


print(f"\n5.")
print(f"Estudio: {model_check(knowledge, estudio)}")
print(f"No paso: {model_check(knowledge, Not(paso))}")
