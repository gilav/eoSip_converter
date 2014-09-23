Distributed computing: run several converter at once on one or several hosts
Based on Pyro example.


Requiere:
 - Pyro4, serpent serializer

To run it do:
 - start naming.py
 - start dispatcher.py
 - start one or several worker_converter, with arguments like:
anapython worker_converter.py C:\Users\glavaux\data\Development\python\eoSip_converter\ingester_tropforest.py C:\Users\glavaux\data\Development\python\eoSip_converter\ingest_dimap_tropforest.cfg 4
 - start ONE client.py, passing in argument the file containing the list of products to be converted.


Gilles Lavaux 09/2014
