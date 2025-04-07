from flask import Flask, request, jsonify, render_template, send_file
import networkx as nx
import matplotlib.pyplot as plt
import tempfile

app = Flask(__name__, template_folder='templates')
G = nx.DiGraph()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/crear_grafo', methods=['POST'])
def crear_grafo():
    G.clear()
    nodos = request.form.getlist('nodos[]')
    descendientes = request.form.getlist('descendientes[]')
    distancias = request.form.getlist('distancias[]')

    for i in range(len(nodos)):
        try:
            lista_descendientes = descendientes[i].split(',')
            lista_distancias = [float(d) for d in distancias[i].split(',')]
            for j in range(len(lista_descendientes)):
                G.add_edge(nodos[i].strip(), lista_descendientes[j].strip(), weight=lista_distancias[j])
        except ValueError:
            return f"Error: Formato inválido en los datos de '{nodos[i]}'.", 400

    return '¡Grafo creado correctamente!'

@app.route('/ruta_corta', methods=['GET'])
def ruta_corta():
    origen = request.args.get('origen')
    destino = request.args.get('destino')
    try:
        camino = nx.dijkstra_path(G, origen, destino)
        distancia = nx.dijkstra_path_length(G, origen, destino)
        return jsonify({'camino': camino, 'distancia': distancia})
    except Exception as e:
        return str(e), 400

@app.route('/grafo_img', methods=['GET'])
def graficar_imagen():
    origen = request.args.get('origen')
    destino = request.args.get('destino')

    
    pos = nx.circular_layout(G)  
    plt.figure(figsize=(6, 6))

    
    nx.draw(G, pos, with_labels=True, node_color='#87CEEB', edge_color='#003366',
            font_weight='bold', node_size=900, font_size=10)
    etiquetas = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=etiquetas, font_color='#003366')

    
    if origen and destino:
        try:
            camino = nx.dijkstra_path(G, origen, destino)
            nx.draw_networkx_nodes(G, pos, nodelist=camino, node_color='red', node_size=1000)
            edges = list(zip(camino, camino[1:]))
            nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color='red', width=2)
        except Exception:
            pass  

    
    temp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    plt.savefig(temp.name)
    plt.close()
    return send_file(temp.name, mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True)
