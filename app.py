from flask import Flask, render_template, request, jsonify
import os
import subprocess
import base64

app = Flask(__name__)

def generate_component_diagram(inputs, interfaces, connections):
    plantuml_code = "@startuml\n\n"

    # Define entities with the given inputs
    for entity in inputs:
        plantuml_code += f"component {entity}\n"

    # Define interfaces
    for entity, interface in interfaces.items():
        interface_name = interface['name']
        if interface.get("provides"):
            plantuml_code += f"{entity} -down-|> {interface_name}\n"
        if interface.get("requires"):
            plantuml_code += f"{entity} -up-.- {interface_name}\n"

    # Define connections
    for conn in connections:
        from_entity = conn['from']
        to_entity = conn['to']
        dashed = conn.get('dashed', False)  # Check if the connection is dashed

        arrow_style = "-->" if not dashed else "-.-"  # Use '-.-' for dashed arrow

        plantuml_code += f"{from_entity} {arrow_style} {to_entity}\n"
    plantuml_code += "\nremove @unlinked"
    plantuml_code += "\n@enduml"

    return plantuml_code


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        num_entities = int(request.form["num_entities"])
        entities = []
        interfaces = {}
        connections = []

        for i in range(num_entities):
            entity_name = request.form.get(f"entity_{i + 1}")
            entities.append(entity_name)

            provides_interface = request.form.get(f"provides_{i + 1}")
            requires_interface = request.form.get(f"requires_{i + 1}")

            if provides_interface or requires_interface:
                interface_name = request.form.get(f"interface_{i + 1}")
                interfaces[entity_name] = {
                    "name": interface_name,
                    "provides": provides_interface,
                    "requires": requires_interface,
                }

        for i in range(num_entities - 1):
            from_entity = request.form.get(f"from_{i + 1}")
            to_entity = request.form.get(f"to_{i + 1}")

            if from_entity and to_entity:
                connections.append({"from": from_entity, "to": to_entity})

        # Generate PlantUML code
        diagram_code = generate_component_diagram(entities, interfaces, connections)

        # Save the PlantUML code to a file
        with open("component_diagram.puml", "w") as file:
            file.write(diagram_code)

        # Render the diagram using PlantUML
        plantuml_path = "D:\Chrome_Downloads\plantuml-1.2023.10.jar"
        subprocess.run(["java", "-jar", plantuml_path, "component_diagram.puml"])

        # Convert the diagram image to base64
        with open("component_diagram.png", "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode()

        # Remove the temporary PlantUML and image files
        os.remove("component_diagram.puml")
        os.remove("component_diagram.png")

        return jsonify({"base64_image": base64_image})

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)


