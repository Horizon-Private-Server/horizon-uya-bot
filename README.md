# thug
Thug is a multiplayer bot written for the PS2 game Ratchet & Clank: Up Your Arsenal. Currently written to connect to the [Robo](https://github.com/jtjanecek/robo) UYA custom server, however it will eventually support the [Horizon Private Server](https://github.com/Horizon-Private-Server/horizon-server) (UYA only). This bot will only work for UYA because the structures that it uses are game specific.

The name Thug comes from the UYA multiplayer skin.

## How does it work?
Thug connects to a Medius server and simulates what a normal PS2 would send over the network. Thug is written in Python and uses the asyncio standard library for network connections. 

Thug builds a network graph based on a set of moveable points, then uses the A* algorithm to pathfind to other players/objects.

Bot Movement Graph             |  In Game View
:-------------------------:|:-------------------------:
<img src="https://raw.githubusercontent.com/jtjanecek/thug/master/assets/scatter_command_center.png" width="455" height="350">  |  <img src="https://raw.githubusercontent.com/jtjanecek/thug/master/assets/command_center.jpg" width="455" height="350">
