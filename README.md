eoSip_converter
===============

This converter can read various Eo-Products and convert them in Eo-Sip format.
Supported products are at this time:
- Ikonos
- Tropforest
- ERS reaper
- Spot




History:
========

2014-05-29: Tropforest is now OGC

2014-05-21: Will move to OGC only spec (drop NgEO). So probably this is the last NgEo uupdate

2014-05-14:
 - support additionnal data provider: CSV files (at this time)
 
2014-05-12:
 - Support alt:nominalTrack for alt: products
 
2014-05-05
- Support eop: alt: opt: typologies in report matadata file

2014-04-28:
 - support local attributes

2014-04-23:
 - Reaper converter works.

2014-04-22:
 - finish browse report footprint block
 - Spot converter ok
 
2014-04-18:
 - generate index file
 
2014-04-17: 
 - implement Tiff convertion using external exec
 - UTM to lat/lon convertion
 ==> Tropforest  converter ok, all products processed

2014-04-15:
 ==> Ikonos converter ok, all products processed
 
 

TODO:
- don't create xml nodes that are optionnal and have None or UKNOWN value
- calculate if reaper footprint is in one or more segments, create alt:nominalTrack accordingly
- add option to move thumbnail + metadataReport in destination folder structure





