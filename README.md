# Onioncrawl
Tor crawler that takes a seed and digs tunnels in the network

The principe is simple. We take a known .onion site and we look for other onions on this onion.
The tool does the same on the next found onion etc.

For now this is single threaded so don't expect impressive speeds from it.

I am still working on a decent way to visualize the results.
For now I am using Pyvis but the performance is rather shaky after a few thousand of hosts.


Disclaimer:
I am not responsible for anything you find and the consequences that follow from that.
The database and the json file might contain text linked to illegal practices.


Usage:

Create a venv:
python3 -m venv venv-onc
pip install -r requirements.txt

source venv-onc/bin/activate
python3 onioncrawl.py

After the run is complete you can run:

python3 grapher.py

python3 -m http.server

Navigate to localhost:8000/graph.html

