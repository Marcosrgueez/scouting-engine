# Auditoría top/bottom-10 de los 5 roles — 6 temporadas

Generado 2026-09-03. Consulta pura sobre `player_role_scores` + `player_role_score_breakdown` (Fase 5). Sin recálculo, sin cambios de pesos ni de esquema.

- **score** = SUM(percentil × peso) / SUM(peso), 0-100, dentro de la competición-temporada.
- **min** = minutos totales del jugador esa temporada (suma de sus etapas).
- **métricas top** = las 3 de mayor contribución del desglose, `code pXX (cNN)` = percentil y contribución (percentil × peso).
- **bottom-10** = los 10 scores más bajos ENTRE LOS QUE TIENEN score en ese rol (no los que no aplican por bucket).


## Distribuciones (media / mediana / desviación por rol-temporada)

| rol | temporada | n | media | mediana | desv | min | max |
|---|---|---|---|---|---|---|---|
| Ball Winner | La Liga 2024/2025 | 216 | 50.0 | 49.9 | 17.4 | 12.1 | 90.1 |
| Ball Winner | La Liga 2025/2026 | 220 | 50.0 | 50.3 | 16.2 | 9.3 | 86.6 |
| Ball Winner | La Liga 2 2025/2026 | 233 | 50.0 | 50.6 | 17.0 | 14.5 | 84.5 |
| Ball Winner | Premier League 2025/2026 | 228 | 50.0 | 51.2 | 17.9 | 8.0 | 86.2 |
| Ball Winner | Serie A 2025/2026 | 238 | 50.0 | 48.6 | 16.9 | 11.0 | 91.0 |
| Ball Winner | Bundesliga 2025/2026 | 195 | 50.0 | 48.7 | 17.2 | 10.6 | 86.1 |
| Deep-Lying Playmaker | La Liga 2024/2025 | 96 | 49.9 | 48.6 | 19.8 | 8.2 | 96.6 |
| Deep-Lying Playmaker | La Liga 2025/2026 | 94 | 49.9 | 48.6 | 19.6 | 5.1 | 95.5 |
| Deep-Lying Playmaker | La Liga 2 2025/2026 | 97 | 48.1 | 46.3 | 15.9 | 20.2 | 78.8 |
| Deep-Lying Playmaker | Premier League 2025/2026 | 101 | 50.0 | 48.0 | 19.1 | 11.3 | 89.1 |
| Deep-Lying Playmaker | Serie A 2025/2026 | 111 | 49.9 | 50.6 | 20.3 | 6.1 | 93.5 |
| Deep-Lying Playmaker | Bundesliga 2025/2026 | 84 | 50.0 | 49.5 | 18.7 | 6.5 | 96.4 |
| Advanced Playmaker | La Liga 2024/2025 | 149 | 49.4 | 50.5 | 22.2 | 3.4 | 97.4 |
| Advanced Playmaker | La Liga 2025/2026 | 150 | 49.3 | 49.5 | 23.2 | 1.7 | 99.7 |
| Advanced Playmaker | La Liga 2 2025/2026 | 171 | 47.5 | 47.7 | 22.4 | 1.9 | 94.1 |
| Advanced Playmaker | Premier League 2025/2026 | 153 | 49.7 | 50.0 | 21.9 | 2.8 | 99.3 |
| Advanced Playmaker | Serie A 2025/2026 | 140 | 49.3 | 48.7 | 22.8 | 4.2 | 97.1 |
| Advanced Playmaker | Bundesliga 2025/2026 | 118 | 49.6 | 46.7 | 23.5 | 2.0 | 97.1 |
| Central Constructor | La Liga 2024/2025 | 63 | 50.0 | 48.2 | 18.5 | 11.2 | 86.5 |
| Central Constructor | La Liga 2025/2026 | 69 | 50.0 | 49.5 | 17.1 | 10.9 | 85.2 |
| Central Constructor | La Liga 2 2025/2026 | 69 | 50.0 | 53.1 | 19.1 | 8.1 | 87.9 |
| Central Constructor | Premier League 2025/2026 | 66 | 50.0 | 51.8 | 17.8 | 9.1 | 83.7 |
| Central Constructor | Serie A 2025/2026 | 72 | 50.0 | 47.0 | 17.9 | 12.7 | 85.0 |
| Central Constructor | Bundesliga 2025/2026 | 63 | 50.0 | 48.4 | 17.0 | 11.1 | 83.2 |
| Central Dominante | La Liga 2024/2025 | 63 | 50.0 | 49.6 | 18.7 | 14.4 | 85.2 |
| Central Dominante | La Liga 2025/2026 | 69 | 50.0 | 51.9 | 17.6 | 9.1 | 89.9 |
| Central Dominante | La Liga 2 2025/2026 | 69 | 50.0 | 52.4 | 18.7 | 13.2 | 87.8 |
| Central Dominante | Premier League 2025/2026 | 66 | 50.0 | 52.8 | 20.0 | 4.4 | 87.8 |
| Central Dominante | Serie A 2025/2026 | 72 | 50.0 | 51.0 | 19.0 | 11.0 | 86.7 |
| Central Dominante | Bundesliga 2025/2026 | 63 | 50.0 | 48.0 | 19.6 | 14.6 | 84.3 |

### Histograma de franjas de 10 puntos

Ver cada rol-temporada abajo. Franja modal y forma:
- Ball Winner / La Liga 2024/2025: 0 6 26 36 42 41 33 21 10 1  (modal 40-50)
- Ball Winner / La Liga 2025/2026: 1 6 16 41 43 51 36 21 5 0  (modal 50-60)
- Ball Winner / La Liga 2 2025/2026: 0 7 26 33 49 53 33 21 11 0  (modal 50-60)
- Ball Winner / Premier League 2025/2026: 2 11 20 33 44 47 33 32 6 0  (modal 50-60)
- Ball Winner / Serie A 2025/2026: 0 7 20 46 52 47 30 27 7 2  (modal 40-50)
- Ball Winner / Bundesliga 2025/2026: 0 8 18 28 49 35 33 16 8 0  (modal 40-50)
- Deep-Lying Playmaker / La Liga 2024/2025: 1 7 9 14 19 14 17 6 7 2  (modal 40-50)
- Deep-Lying Playmaker / La Liga 2025/2026: 2 4 9 12 23 18 8 12 5 1  (modal 40-50)
- Deep-Lying Playmaker / La Liga 2 2025/2026: 0 0 11 23 18 21 13 11 0 0  (modal 30-40)
- Deep-Lying Playmaker / Premier League 2025/2026: 0 6 11 13 23 20 8 13 7 0  (modal 40-50)
- Deep-Lying Playmaker / Serie A 2025/2026: 2 7 13 13 20 18 21 11 4 2  (modal 60-70)
- Deep-Lying Playmaker / Bundesliga 2025/2026: 1 3 10 9 21 18 9 8 3 2  (modal 40-50)
- Advanced Playmaker / La Liga 2024/2025: 6 8 19 19 20 35 13 12 11 6  (modal 50-60)
- Advanced Playmaker / La Liga 2025/2026: 5 11 18 22 20 22 15 22 11 4  (modal 30-40)
- Advanced Playmaker / La Liga 2 2025/2026: 8 13 22 27 24 23 24 14 14 2  (modal 30-40)
- Advanced Playmaker / Premier League 2025/2026: 4 13 13 23 24 17 32 16 8 3  (modal 60-70)
- Advanced Playmaker / Serie A 2025/2026: 4 11 22 13 22 14 28 14 5 7  (modal 60-70)
- Advanced Playmaker / Bundesliga 2025/2026: 4 11 13 13 22 11 15 13 14 2  (modal 40-50)
- Central Constructor / La Liga 2024/2025: 0 2 7 11 14 9 9 7 4 0  (modal 40-50)
- Central Constructor / La Liga 2025/2026: 0 3 6 11 16 11 14 4 4 0  (modal 40-50)
- Central Constructor / La Liga 2 2025/2026: 1 4 8 7 11 17 11 6 4 0  (modal 50-60)
- Central Constructor / Premier League 2025/2026: 1 3 6 8 12 17 9 7 3 0  (modal 50-60)
- Central Constructor / Serie A 2025/2026: 0 3 9 9 18 10 11 9 3 0  (modal 40-50)
- Central Constructor / Bundesliga 2025/2026: 0 1 6 16 9 7 17 5 2 0  (modal 60-70)
- Central Dominante / La Liga 2024/2025: 0 3 7 13 9 10 9 8 4 0  (modal 30-40)
- Central Dominante / La Liga 2025/2026: 1 4 1 16 10 15 13 6 3 0  (modal 30-40)
- Central Dominante / La Liga 2 2025/2026: 0 4 8 12 10 13 10 10 2 0  (modal 50-60)
- Central Dominante / Premier League 2025/2026: 1 5 5 14 4 14 12 7 4 0  (modal 30-40)
- Central Dominante / Serie A 2025/2026: 0 3 12 7 12 15 13 5 5 0  (modal 50-60)
- Central Dominante / Bundesliga 2025/2026: 0 5 6 11 12 7 11 6 5 0  (modal 40-50)

### Anomalías puramente estadísticas

- Deep-Lying Playmaker / La Liga 2 2025/2026: rango [20.2, 78.8] (sd 15.9) — sin extremos; el mismo rol en las otras 5 temporadas llega a [5-11, 89-97]
- Todas las combinaciones rol-temporada: media ≈ 50.0 (±2.5) y mediana a <4 de la media → distribuciones centradas y casi simétricas. Es por construcción (el score es una media ponderada de percentiles, que son ~uniformes 0-100).


---

## Ball Winner

### La Liga 2024/2025

n = 216 · media 50.0 · mediana 49.9 · desv 17.4 · rango [12.1, 90.1]

```
    0-10  |  0
   10-20  | #### 6
   20-30  | ################# 26
   30-40  | ######################## 36
   40-50  | ############################ 42
   50-60  | ########################### 41
   60-70  | ###################### 33
   70-80  | ############## 21
   80-90  | ####### 10
   90-100 | # 1
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Eduardo Camavinga | Real Madrid | 90.1 | 1098 | duels-won p100 (c300), tackles p100 (c300), interceptions p91 (c272) |
| 2 | Jorge Sáenz | Leganés | 85.1 | 1691 | duels-won p95 (c285), tackles p92 (c276), interceptions p84 (c252) |
| 3 | Omar El Hilali | Espanyol | 83.7 | 3160 | tackles p98 (c295), interceptions p86 (c257), duels-won p86 (c257) |
| 4 | Nahuel Tenaglia | Deportivo Alavés | 83.6 | 2924 | tackles p96 (c289), duels-won p95 (c284), interceptions p93 (c279) |
| 5 | Lucien Agoumé | Sevilla | 81.8 | 2123 | interceptions p97 (c291), tackles p94 (c281), duels-won p72 (c215) |
| 6 | Stefan Bajcetic | Las Palmas | 80.9 | 976 | interceptions p91 (c272), duels-won p89 (c268), tackles p82 (c246) |
| 7 | Samú Costa | Mallorca | 80.8 | 2655 | duels-won p96 (c287), tackles p92 (c275), interceptions p64 (c193) |
| 8 | Jon Aramburu | Real Sociedad | 80.8 | 2463 | tackles p100 (c300), duels-won p100 (c300), interceptions p75 (c225) |
| 9 | Marc Bartra | Real Betis | 80.5 | 2101 | interceptions p94 (c281), duels-won p71 (c213), tackles p68 (c203) |
| 10 | Dário Essugo | Las Palmas | 80.3 | 1951 | interceptions p98 (c294), tackles p84 (c253), duels-won p76 (c227) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Jesús Areso | Osasuna | 21.8 | 3088 | clearances p50 (c75), tackles p25 (c75), duels-won p20 (c59) |
| 2 | Unai Gómez | Athletic Club | 21.3 | 1280 | duels-won p37 (c111), yellowcards p97 (c48), clearances p31 (c46) |
| 3 | Sergi Darder | Mallorca | 21.3 | 2765 | interceptions p21 (c63), duels-won p18 (c54), fouls p93 (c46) |
| 4 | Hugo Sotelo | Celta de Vigo | 20.0 | 1262 | tackles p48 (c145), blocked-shots p16 (c24), fouls p47 (c24) |
| 5 | Brian Oliván | Espanyol | 19.9 | 1018 | interceptions p38 (c112), blocked-shots p27 (c40), yellowcards p62 (c31) |
| 6 | Fermín López | FC Barcelona | 19.1 | 1256 | duels-won p51 (c152), tackles p14 (c41), interceptions p8 (c25) |
| 7 | Rodrigo De Paul | Atlético de Madrid | 18.9 | 2111 | duels-won p24 (c73), tackles p16 (c47), fouls p89 (c45) |
| 8 | Dakonam Djené | Getafe | 17.3 | 2555 | duels-won p26 (c77), interceptions p24 (c73), tackles p11 (c34) |
| 9 | Antonio Rüdiger | Real Madrid | 15.0 | 2290 | fouls p84 (c42), blocked-shots p27 (c41), yellowcards p79 (c40) |
| 10 | Oihan Sancet | Athletic Club | 12.1 | 1624 | duels-won p16 (c47), yellowcards p86 (c43), fouls p85 (c43) |

### La Liga 2025/2026

n = 220 · media 50.0 · mediana 50.3 · desv 16.2 · rango [9.3, 86.6]

```
    0-10  | # 1
   10-20  | ### 6
   20-30  | ######### 16
   30-40  | ####################### 41
   40-50  | ######################## 43
   50-60  | ############################ 51
   60-70  | #################### 36
   70-80  | ############ 21
   80-90  | ### 5
   90-100 |  0
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Sergi Altimira | Real Betis | 86.6 | 1183 | tackles p100 (c300), interceptions p96 (c287), duels-won p96 (c287) |
| 2 | Kike Salas | Sevilla | 86.1 | 2202 | duels-won p100 (c300), tackles p93 (c278), interceptions p91 (c274) |
| 3 | Óscar Valentín | Rayo Vallecano | 84.0 | 2118 | tackles p96 (c287), interceptions p85 (c255), duels-won p69 (c206) |
| 4 | Aurélien Tchouaméni | Real Madrid | 81.6 | 2624 | interceptions p99 (c297), duels-won p80 (c239), tackles p77 (c232) |
| 5 | Pathé Ciss | Rayo Vallecano | 81.1 | 1993 | interceptions p98 (c294), tackles p87 (c261), duels-won p59 (c177) |
| 6 | David Affengruber | Elche | 79.7 | 2952 | tackles p91 (c274), duels-won p91 (c274), interceptions p90 (c269) |
| 7 | Diego Llorente | Real Betis | 79.5 | 1229 | interceptions p100 (c300), duels-won p82 (c247), tackles p79 (c238) |
| 8 | Jon Aramburu | Real Sociedad | 79.5 | 2778 | tackles p95 (c284), duels-won p93 (c279), interceptions p91 (c273) |
| 9 | Marc Bartra | Real Betis | 79.2 | 1976 | tackles p84 (c251), interceptions p69 (c207), duels-won p69 (c207) |
| 10 | Eduardo Camavinga | Real Madrid | 79.0 | 1525 | tackles p99 (c297), duels-won p92 (c277), interceptions p57 (c171) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Trent Alexander-Arnold | Real Madrid | 21.1 | 1164 | interceptions p54 (c161), blocked-shots p39 (c59), fouls p82 (c41) |
| 2 | Dimitri Foulquier | Valencia | 20.8 | 1148 | clearances p75 (c112), interceptions p16 (c48), yellowcards p95 (c47) |
| 3 | Pablo Marín | Real Sociedad | 20.3 | 1494 | duels-won p26 (c77), clearances p33 (c50), interceptions p15 (c45) |
| 4 | Carlos Álvarez | Levante | 19.6 | 1900 | duels-won p32 (c97), interceptions p24 (c71), fouls p75 (c38) |
| 5 | Oihan Sancet | Athletic Club | 18.4 | 1802 | duels-won p34 (c103), tackles p13 (c39), blocked-shots p22 (c32) |
| 6 | Martim Neto | Elche | 17.8 | 1352 | duels-won p20 (c61), tackles p18 (c55), clearances p32 (c48) |
| 7 | Youssef Enríquez | Deportivo Alavés | 15.8 | 1340 | interceptions p21 (c64), clearances p39 (c59), duels-won p18 (c54) |
| 8 | Unai Gómez | Athletic Club | 14.9 | 977 | duels-won p18 (c55), yellowcards p87 (c44), fouls p69 (c34) |
| 9 | Raúl Asencio | Real Madrid | 13.3 | 1707 | blocked-shots p43 (c64), fouls p72 (c36), yellowcards p50 (c25) |
| 10 | Antonio Rüdiger | Real Madrid | 9.3 | 1491 | yellowcards p100 (c50), fouls p93 (c46), tackles p3 (c9) |

### La Liga 2 2025/2026

n = 233 · media 50.0 · mediana 50.6 · desv 17.0 · rango [14.5, 84.5]

```
    0-10  |  0
   10-20  | #### 7
   20-30  | ############## 26
   30-40  | ################# 33
   40-50  | ########################## 49
   50-60  | ############################ 53
   60-70  | ################# 33
   70-80  | ########### 21
   80-90  | ###### 11
   90-100 |  0
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Lorenzo Amatucci | Las Palmas | 84.5 | 3511 | tackles p99 (c297), duels-won p94 (c281), interceptions p77 (c231) |
| 2 | Sergio Álvarez | SD Eibar | 84.3 | 2796 | tackles p97 (c291), duels-won p88 (c262), interceptions p73 (c219) |
| 3 | Juanpe Jiménez | Málaga | 84.1 | 1017 | tackles p100 (c300), duels-won p98 (c294), interceptions p97 (c291) |
| 4 | Miguel Atienza | Burgos | 83.5 | 3516 | interceptions p100 (c300), tackles p78 (c234), duels-won p77 (c231) |
| 5 | Stanko Juric | Real Valladolid | 83.3 | 3027 | interceptions p99 (c297), duels-won p97 (c291), tackles p94 (c281) |
| 6 | Carlos Puga | Málaga | 83.0 | 2950 | tackles p100 (c300), duels-won p97 (c291), interceptions p88 (c264) |
| 7 | Unax Agote | Real Sociedad II | 82.6 | 1385 | duels-won p98 (c295), tackles p88 (c264), interceptions p85 (c255) |
| 8 | Lander Olaetxea | SD Eibar | 82.5 | 1556 | tackles p92 (c275), interceptions p88 (c262), duels-won p80 (c241) |
| 9 | Iza Carcelén | Cádiz | 82.3 | 2364 | tackles p95 (c286), duels-won p91 (c273), interceptions p77 (c232) |
| 10 | Xavi Sintes | Córdoba | 80.9 | 2078 | interceptions p97 (c291), tackles p94 (c282), duels-won p88 (c265) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Javi Hernández | Mirandés | 22.0 | 1861 | duels-won p64 (c191), blocked-shots p24 (c36), clearances p12 (c19) |
| 2 | Izan Merino | Málaga | 21.8 | 2934 | clearances p56 (c84), interceptions p22 (c66), blocked-shots p35 (c53) |
| 3 | Francho Serrano | Real Zaragoza | 20.6 | 2887 | clearances p54 (c81), yellowcards p100 (c50), fouls p99 (c49) |
| 4 | Baïla Diallo | Granada | 19.2 | 2559 | clearances p55 (c82), interceptions p12 (c36), duels-won p12 (c36) |
| 5 | Théo Le Normand | FC Andorra | 19.1 | 1106 | interceptions p25 (c75), clearances p42 (c63), duels-won p20 (c59) |
| 6 | Chuki | Real Valladolid | 17.5 | 2339 | duels-won p41 (c122), yellowcards p82 (c41), interceptions p9 (c28) |
| 7 | Sergio Arribas | Almería | 16.8 | 3812 | duels-won p22 (c66), fouls p97 (c48), yellowcards p95 (c47) |
| 8 | Iván Gil | Las Palmas | 16.6 | 941 | blocked-shots p39 (c58), clearances p34 (c52), fouls p88 (c44) |
| 9 | Agus Medina | Albacete | 15.5 | 2076 | tackles p20 (c59), yellowcards p97 (c48), fouls p62 (c31) |
| 10 | Brian Oliván | Sporting Gijón | 14.5 | 1139 | clearances p80 (c120), fouls p89 (c45), yellowcards p29 (c14) |

### Premier League 2025/2026

n = 228 · media 50.0 · mediana 51.2 · desv 17.9 · rango [8.0, 86.2]

```
    0-10  | # 2
   10-20  | ####### 11
   20-30  | ############ 20
   30-40  | #################### 33
   40-50  | ########################## 44
   50-60  | ############################ 47
   60-70  | #################### 33
   70-80  | ################### 32
   80-90  | #### 6
   90-100 |  0
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | João Palhinha | Tottenham Hotspur | 86.2 | 2197 | tackles p100 (c300), duels-won p99 (c297), interceptions p78 (c234) |
| 2 | Joël Veltman | Brighton & Hove Albion | 85.4 | 1048 | interceptions p95 (c285), duels-won p93 (c280), tackles p80 (c240) |
| 3 | Kenny Tete | Fulham | 83.5 | 1796 | tackles p100 (c300), duels-won p97 (c290), interceptions p83 (c250) |
| 4 | Florentino | Burnley | 83.4 | 2116 | interceptions p98 (c294), tackles p97 (c291), duels-won p68 (c204) |
| 5 | James Justin | Leeds United | 83.0 | 1897 | duels-won p88 (c265), tackles p78 (c235), interceptions p77 (c230) |
| 6 | Amadou Onana | Aston Villa | 80.0 | 1778 | duels-won p81 (c243), interceptions p77 (c231), tackles p69 (c207) |
| 7 | Soungoutou Magassa | West Ham United | 79.9 | 979 | tackles p96 (c288), interceptions p92 (c276), duels-won p87 (c261) |
| 8 | Casemiro | Manchester United | 78.5 | 2589 | tackles p91 (c273), duels-won p85 (c255), interceptions p61 (c183) |
| 9 | James Hill | AFC Bournemouth | 76.9 | 2112 | duels-won p97 (c291), interceptions p94 (c282), tackles p71 (c212) |
| 10 | Tim Iroegbunam | Everton | 76.8 | 1487 | duels-won p98 (c294), tackles p98 (c294), interceptions p82 (c246) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Morgan Rogers | Aston Villa | 17.4 | 3285 | duels-won p29 (c87), clearances p19 (c28), yellowcards p55 (c28) |
| 2 | Florian Wirtz | Liverpool | 17.2 | 2389 | yellowcards p93 (c46), duels-won p15 (c45), fouls p79 (c40) |
| 3 | Jack Hinshelwood | Brighton & Hove Albion | 16.9 | 1750 | blocked-shots p47 (c70), clearances p44 (c66), yellowcards p100 (c50) |
| 4 | Morgan Gibbs-White | Nottingham Forest | 16.5 | 3112 | duels-won p16 (c48), yellowcards p94 (c47), fouls p90 (c45) |
| 5 | David Møller Wolfe | Wolverhampton Wanderers | 15.3 | 1049 | clearances p37 (c55), yellowcards p90 (c45), fouls p68 (c34) |
| 6 | Tijjani Reijnders | Manchester City | 15.2 | 1636 | interceptions p18 (c54), clearances p35 (c52), yellowcards p76 (c38) |
| 7 | Victor Lindelöf | Aston Villa | 14.8 | 944 | interceptions p22 (c65), fouls p100 (c50), yellowcards p100 (c50) |
| 8 | Martin Ødegaard | Arsenal | 13.4 | 1370 | yellowcards p100 (c50), fouls p98 (c49), interceptions p12 (c36) |
| 9 | Justin Kluivert | AFC Bournemouth | 9.2 | 952 | blocked-shots p34 (c51), duels-won p9 (c27), interceptions p7 (c21) |
| 10 | Habib Diarra | Sunderland | 8.0 | 1408 | duels-won p14 (c42), clearances p18 (c27), fouls p41 (c20) |

### Serie A 2025/2026

n = 238 · media 50.0 · mediana 48.6 · desv 16.9 · rango [11.0, 91.0]

```
    0-10  |  0
   10-20  | #### 7
   20-30  | ########### 20
   30-40  | ######################### 46
   40-50  | ############################ 52
   50-60  | ######################### 47
   60-70  | ################ 30
   70-80  | ############### 27
   80-90  | #### 7
   90-100 | # 2
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Patrizio Masini | Genoa | 91.0 | 1399 | duels-won p100 (c300), tackles p100 (c300), interceptions p96 (c289) |
| 2 | Roberto Gagliardini | Hellas Verona | 90.5 | 2213 | interceptions p100 (c300), tackles p97 (c292), duels-won p95 (c286) |
| 3 | Devyne Rensch | Roma | 86.1 | 1178 | interceptions p98 (c294), tackles p89 (c267), duels-won p80 (c239) |
| 4 | Manuel Locatelli | Juventus | 83.9 | 3006 | tackles p98 (c295), interceptions p85 (c254), duels-won p79 (c237) |
| 5 | Victor Nelsson | Hellas Verona | 83.3 | 3316 | interceptions p97 (c292), duels-won p94 (c283), tackles p80 (c241) |
| 6 | Danilo Veiga | Lecce | 82.8 | 3021 | tackles p98 (c294), duels-won p96 (c289), interceptions p67 (c200) |
| 7 | Morten Frendrup | Genoa | 82.1 | 3089 | tackles p96 (c289), interceptions p88 (c265), duels-won p65 (c196) |
| 8 | Jean-Daniel Akpa Akpro | Hellas Verona | 81.8 | 1511 | duels-won p95 (c284), tackles p92 (c275), interceptions p92 (c275) |
| 9 | Martin Frese | Hellas Verona | 80.2 | 2414 | tackles p100 (c300), duels-won p83 (c250), interceptions p83 (c250) |
| 10 | Andrias Edmundsson | Hellas Verona | 79.4 | 1320 | interceptions p96 (c287), tackles p70 (c211), duels-won p65 (c194) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Davide Zappacosta | Atalanta | 23.4 | 2580 | interceptions p40 (c120), clearances p49 (c74), fouls p91 (c45) |
| 2 | Mërgim Vojvoda | Como | 22.8 | 1595 | interceptions p46 (c139), yellowcards p94 (c47), fouls p70 (c35) |
| 3 | Alessandro Marcandalli | Genoa | 22.6 | 2600 | tackles p24 (c72), duels-won p18 (c55), fouls p90 (c45) |
| 4 | Fisayo Dele-Bashiru | Lazio | 19.8 | 1180 | tackles p35 (c104), yellowcards p100 (c50), fouls p95 (c47) |
| 5 | Enzo Ebosse | Hellas Verona | 19.3 | 1334 | blocked-shots p83 (c125), clearances p31 (c46), tackles p11 (c34) |
| 6 | Sam Beukema | Napoli | 17.8 | 1679 | tackles p20 (c59), blocked-shots p32 (c49), yellowcards p80 (c40) |
| 7 | Luis Henrique | Inter | 16.1 | 1621 | tackles p17 (c52), fouls p100 (c50), yellowcards p90 (c45) |
| 8 | Leonardo Spinazzola | Napoli | 14.2 | 1905 | fouls p94 (c47), tackles p13 (c39), yellowcards p76 (c38) |
| 9 | Marcus Pedersen | Torino | 12.0 | 2134 | blocked-shots p39 (c58), interceptions p11 (c33), yellowcards p61 (c31) |
| 10 | Kevin De Bruyne | Napoli | 11.0 | 1169 | fouls p94 (c47), yellowcards p84 (c42), interceptions p12 (c35) |

### Bundesliga 2025/2026

n = 195 · media 50.0 · mediana 48.7 · desv 17.2 · rango [10.6, 86.1]

```
    0-10  |  0
   10-20  | ##### 8
   20-30  | ########## 18
   30-40  | ################ 28
   40-50  | ############################ 49
   50-60  | #################### 35
   60-70  | ################### 33
   70-80  | ######### 16
   80-90  | ##### 8
   90-100 |  0
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Bernardo | TSG Hoffenheim | 86.1 | 2321 | duels-won p100 (c300), interceptions p89 (c268), tackles p87 (c262) |
| 2 | Vinicius de Souza Costa | VfL Wolfsburg | 85.5 | 1773 | duels-won p99 (c296), tackles p95 (c286), interceptions p82 (c246) |
| 3 | Lars Ritzka | St. Pauli | 84.9 | 970 | tackles p100 (c300), interceptions p96 (c287), duels-won p74 (c223) |
| 4 | Lukas Kübler | SC Freiburg | 84.5 | 1594 | interceptions p100 (c300), duels-won p79 (c236), tackles p79 (c236) |
| 5 | Tom Krauß | FC Köln | 84.4 | 1784 | tackles p100 (c300), duels-won p84 (c253), interceptions p83 (c249) |
| 6 | Maximilian Mittelstädt | VfB Stuttgart | 84.0 | 2190 | tackles p94 (c281), duels-won p94 (c281), interceptions p94 (c281) |
| 7 | Chema Andrés | VfB Stuttgart | 83.9 | 1307 | interceptions p99 (c296), duels-won p87 (c260), tackles p77 (c231) |
| 8 | Philipp Sander | Borussia Mönchengladbach | 80.3 | 2456 | interceptions p93 (c278), tackles p89 (c267), duels-won p70 (c210) |
| 9 | Jackson Irvine | St. Pauli | 79.4 | 1625 | interceptions p88 (c264), duels-won p80 (c239), tackles p67 (c202) |
| 10 | András Schäfer | FC Union Berlin | 79.4 | 1427 | tackles p93 (c278), duels-won p88 (c264), interceptions p87 (c260) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Hiroki Ito | FC Bayern München | 21.1 | 921 | interceptions p61 (c184), yellowcards p100 (c50), fouls p47 (c23) |
| 2 | Ísak Jóhannesson | FC Köln | 20.2 | 1813 | blocked-shots p59 (c89), tackles p20 (c61), fouls p77 (c39) |
| 3 | Julian Ryerson | Borussia Dortmund | 19.1 | 2273 | duels-won p32 (c96), interceptions p17 (c51), tackles p13 (c38) |
| 4 | Derrick Köhn | FC Union Berlin | 18.8 | 1902 | tackles p32 (c96), blocked-shots p34 (c51), duels-won p13 (c38) |
| 5 | Edmond Tapsoba | Bayer 04 Leverkusen | 18.4 | 2576 | blocked-shots p35 (c53), tackles p18 (c53), duels-won p16 (c48) |
| 6 | Christian Günter | SC Freiburg | 17.4 | 1549 | blocked-shots p62 (c93), fouls p81 (c40), interceptions p11 (c32) |
| 7 | Joël Schmied | FC Köln | 14.0 | 1081 | blocked-shots p61 (c92), interceptions p11 (c34), tackles p8 (c24) |
| 8 | Julian Brandt | Borussia Dortmund | 13.6 | 1606 | duels-won p17 (c51), yellowcards p100 (c50), fouls p92 (c46) |
| 9 | Jonas Hofmann | Bayer 04 Leverkusen | 12.5 | 1009 | fouls p93 (c46), clearances p30 (c45), tackles p12 (c36) |
| 10 | Danel Sinani | St. Pauli | 10.6 | 2071 | duels-won p16 (c47), tackles p8 (c25), yellowcards p47 (c24) |


---

## Deep-Lying Playmaker

### La Liga 2024/2025

n = 96 · media 49.9 · mediana 48.6 · desv 19.8 · rango [8.2, 96.6]

```
    0-10  | # 1
   10-20  | ########## 7
   20-30  | ############# 9
   30-40  | ##################### 14
   40-50  | ############################ 19
   50-60  | ##################### 14
   60-70  | ######################### 17
   70-80  | ######### 6
   80-90  | ########## 7
   90-100 | ### 2
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Luka Modrić | Real Madrid | 96.6 | 1817 | key-passes p99 (c297), passes p99 (c297), accurate-passes-percentage p93 (c278) |
| 2 | Pedri | FC Barcelona | 90.0 | 2897 | passes p97 (c291), key-passes p94 (c281), accurate-passes-percentage p81 (c243) |
| 3 | Dani Ceballos | Real Madrid | 87.2 | 1219 | passes p100 (c300), accurate-passes-percentage p100 (c300), key-passes p80 (c240) |
| 4 | Frenkie de Jong | FC Barcelona | 84.2 | 1131 | accurate-passes-percentage p99 (c297), passes p98 (c294), key-passes p83 (c249) |
| 5 | Damián Rodríguez | Celta de Vigo | 83.1 | 935 | passes p96 (c287), accurate-passes-percentage p95 (c284), key-passes p81 (c243) |
| 6 | Isco | Real Betis | 82.2 | 1550 | key-passes p100 (c300), passes p85 (c256), accurate-passes-percentage p64 (c193) |
| 7 | Arda Güler | Real Madrid | 81.3 | 1248 | key-passes p98 (c294), accurate-passes-percentage p86 (c259), passes p79 (c237) |
| 8 | Federico Valverde | Real Madrid | 81.1 | 3036 | accurate-passes-percentage p91 (c272), passes p87 (c262), key-passes p63 (c189) |
| 9 | Hugo Sotelo | Celta de Vigo | 80.9 | 1262 | passes p92 (c275), key-passes p76 (c227), accurate-passes-percentage p76 (c227) |
| 10 | Rodrigo De Paul | Atlético de Madrid | 77.3 | 2111 | passes p93 (c278), key-passes p86 (c259), long-balls p96 (c144) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Ramón Terrats | Villarreal | 25.6 | 1359 | key-passes p61 (c183), long-balls p40 (c60), through-balls p76 (c38) |
| 2 | Antonio Sánchez | Mallorca | 23.5 | 1386 | long-balls p72 (c107), long-balls-won p43 (c65), passes p13 (c38) |
| 3 | Urko González de Zárate | Real Sociedad | 19.8 | 1428 | key-passes p27 (c82), accurate-passes-percentage p14 (c41), long-balls-won p26 (c39) |
| 4 | Mauro Arambarri | Getafe | 17.2 | 2665 | key-passes p29 (c88), long-balls p44 (c66), passes p6 (c19) |
| 5 | Pablo Ibáñez | Osasuna | 17.2 | 1288 | passes p18 (c54), interceptions p76 (c38), long-balls p22 (c33) |
| 6 | Jon Guridi | Deportivo Alavés | 14.7 | 2099 | key-passes p38 (c114), passes p12 (c35), accurate-passes-percentage p6 (c19) |
| 7 | Unai Gómez | Athletic Club | 13.7 | 1280 | key-passes p40 (c120), accurate-passes-percentage p9 (c28), through-balls p39 (c19) |
| 8 | Alex Král | Espanyol | 13.2 | 2709 | through-balls p77 (c38), long-balls p20 (c30), key-passes p9 (c28) |
| 9 | Darko Brasanac | Leganés | 12.3 | 1614 | key-passes p14 (c41), accurate-passes-percentage p13 (c38), interceptions p48 (c24) |
| 10 | Randy Nteka | Rayo Vallecano | 8.2 | 1153 | key-passes p35 (c104), interceptions p4 (c2), through-balls p0 (c0) |

### La Liga 2025/2026

n = 94 · media 49.9 · mediana 48.6 · desv 19.6 · rango [5.1, 95.5]

```
    0-10  | ## 2
   10-20  | ##### 4
   20-30  | ########### 9
   30-40  | ############### 12
   40-50  | ############################ 23
   50-60  | ###################### 18
   60-70  | ########## 8
   70-80  | ############### 12
   80-90  | ###### 5
   90-100 | # 1
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Pedri | FC Barcelona | 95.5 | 2111 | passes p100 (c300), key-passes p97 (c290), accurate-passes-percentage p96 (c287) |
| 2 | Koke | Atlético de Madrid | 87.5 | 2220 | accurate-passes-percentage p98 (c294), passes p97 (c290), key-passes p69 (c206) |
| 3 | Arda Güler | Real Madrid | 86.3 | 2028 | key-passes p100 (c300), passes p88 (c265), accurate-passes-percentage p87 (c261) |
| 4 | Hugo Sotelo | Celta de Vigo | 86.2 | 1342 | accurate-passes-percentage p99 (c297), passes p96 (c287), key-passes p81 (c242) |
| 5 | Frenkie de Jong | FC Barcelona | 83.1 | 1630 | accurate-passes-percentage p100 (c300), passes p99 (c297), key-passes p87 (c261) |
| 6 | Unai López | Rayo Vallecano | 80.8 | 1619 | key-passes p90 (c271), passes p87 (c261), accurate-passes-percentage p57 (c171) |
| 7 | Pablo Fornals | Real Betis | 79.4 | 2846 | key-passes p98 (c294), passes p83 (c248), accurate-passes-percentage p59 (c177) |
| 8 | Eduardo Camavinga | Real Madrid | 77.7 | 1525 | accurate-passes-percentage p97 (c290), passes p92 (c277), long-balls-won p88 (c132) |
| 9 | Dani Parejo | Villarreal | 77.3 | 1395 | passes p85 (c255), key-passes p74 (c223), accurate-passes-percentage p70 (c210) |
| 10 | Moi Gómez | Osasuna | 76.1 | 1196 | passes p94 (c281), accurate-passes-percentage p76 (c229), key-passes p58 (c174) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Oihan Sancet | Athletic Club | 24.7 | 1802 | key-passes p63 (c190), accurate-passes-percentage p22 (c65), through-balls p41 (c20) |
| 2 | Kwasi Sibo | Real Oviedo | 24.5 | 1688 | accurate-passes-percentage p60 (c181), passes p15 (c45), long-balls-won p27 (c40) |
| 3 | Ramón Terrats | Espanyol | 23.3 | 1025 | key-passes p67 (c200), interceptions p68 (c34), accurate-passes-percentage p6 (c19) |
| 4 | Leander Dendoncker | Real Oviedo | 20.8 | 1333 | accurate-passes-percentage p48 (c145), passes p19 (c58), key-passes p10 (c29) |
| 5 | Jon Guridi | Deportivo Alavés | 17.5 | 1240 | key-passes p33 (c100), accurate-passes-percentage p26 (c77), passes p9 (c26) |
| 6 | Urko González de Zárate | Real Sociedad | 16.6 | 2631 | accurate-passes-percentage p18 (c55), long-balls p29 (c44), interceptions p80 (c40) |
| 7 | Pablo Marín | Real Sociedad | 13.4 | 1494 | key-passes p32 (c97), accurate-passes-percentage p11 (c32), through-balls p47 (c24) |
| 8 | Mauro Arambarri | Getafe | 10.6 | 3255 | key-passes p19 (c58), long-balls p15 (c23), long-balls-won p15 (c23) |
| 9 | Unai Gómez | Athletic Club | 6.7 | 977 | key-passes p25 (c74), accurate-passes-percentage p3 (c10), long-balls p1 (c2) |
| 10 | Mario Martín | Getafe | 5.1 | 2136 | interceptions p31 (c16), key-passes p4 (c13), passes p4 (c13) |

### La Liga 2 2025/2026

n = 97 · media 48.1 · mediana 46.3 · desv 15.9 · rango [20.2, 78.8]

```
    0-10  |  0
   10-20  |  0
   20-30  | ############# 11
   30-40  | ############################ 23
   40-50  | ###################### 18
   50-60  | ########################## 21
   60-70  | ################ 13
   70-80  | ############# 11
   80-90  |  0
   90-100 |  0
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Marc Doménech | FC Andorra | 78.8 | 2288 | accurate-passes-percentage p97 (c291), passes p89 (c266), key-passes p71 (c212) |
| 2 | Manu Trigueros | Granada | 78.3 | 1079 | key-passes p93 (c278), passes p91 (c272), accurate-passes-percentage p59 (c178) |
| 3 | Aleix Garrido | SD Eibar | 77.7 | 2107 | accurate-passes-percentage p98 (c294), passes p94 (c281), key-passes p76 (c228) |
| 4 | Mario Soriano | Deportivo A Coruña | 77.7 | 3616 | accurate-passes-percentage p100 (c300), passes p86 (c259), key-passes p74 (c222) |
| 5 | Bicho | Cultural Leonesa | 77.3 | 2168 | passes p88 (c262), accurate-passes-percentage p79 (c238), key-passes p77 (c231) |
| 6 | Sergio Molina | FC Andorra | 76.6 | 2652 | passes p95 (c284), accurate-passes-percentage p95 (c284), long-balls-won p95 (c142) |
| 7 | Marino Illescas | Ceuta | 75.5 | 1951 | passes p90 (c269), key-passes p78 (c234), accurate-passes-percentage p61 (c184) |
| 8 | Damián Rodríguez | Racing Santander | 74.0 | 966 | passes p97 (c291), accurate-passes-percentage p96 (c287), key-passes p65 (c194) |
| 9 | Julien Ponceau | Real Valladolid | 73.6 | 2450 | accurate-passes-percentage p85 (c256), passes p82 (c247), key-passes p61 (c184) |
| 10 | Seydouba Cissé | Leganés | 72.8 | 2483 | passes p81 (c244), key-passes p68 (c203), accurate-passes-percentage p68 (c203) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Javi Mier | Huesca | 25.1 | 916 | long-balls p73 (c109), long-balls-won p51 (c77), passes p20 (c59) |
| 2 | Sergi Maestre | Cultural Leonesa | 23.3 | 1112 | accurate-passes-percentage p36 (c109), passes p30 (c91), interceptions p91 (c45) |
| 3 | Javi Hernández | Mirandés | 23.2 | 1861 | key-passes p90 (c269), accurate-passes-percentage p7 (c22), long-balls p5 (c8) |
| 4 | Chuki | Real Valladolid | 22.4 | 2339 | key-passes p85 (c256), long-balls p9 (c14), long-balls-won p4 (c6) |
| 5 | Yussi Diarra | Cádiz | 21.2 | 1579 | accurate-passes-percentage p52 (c156), key-passes p24 (c72), interceptions p64 (c32) |
| 6 | Thiago Helguera | Mirandés | 20.7 | 2401 | long-balls-won p48 (c72), key-passes p20 (c59), long-balls p32 (c48) |
| 7 | Gorka Gorosabel | Real Sociedad II | 20.7 | 1118 | key-passes p40 (c119), long-balls p50 (c75), long-balls-won p41 (c61) |
| 8 | Ander Madariaga | SD Eibar | 20.6 | 1678 | key-passes p29 (c88), accurate-passes-percentage p23 (c69), passes p10 (c31) |
| 9 | Théo Le Normand | FC Andorra | 20.2 | 1106 | key-passes p62 (c188), accurate-passes-percentage p15 (c44), interceptions p25 (c12) |
| 10 | Justin Smith | Sporting Gijón | 20.2 | 1830 | accurate-passes-percentage p31 (c94), passes p16 (c47), long-balls p29 (c44) |

### Premier League 2025/2026

n = 101 · media 50.0 · mediana 48.0 · desv 19.1 · rango [11.3, 89.1]

```
    0-10  |  0
   10-20  | ####### 6
   20-30  | ############# 11
   30-40  | ################ 13
   40-50  | ############################ 23
   50-60  | ######################## 20
   60-70  | ########## 8
   70-80  | ################ 13
   80-90  | ######### 7
   90-100 |  0
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Rodri | Manchester City | 89.1 | 1513 | passes p100 (c300), accurate-passes-percentage p94 (c282), key-passes p73 (c219) |
| 2 | Dominik Szoboszlai | Liverpool | 86.8 | 3233 | key-passes p93 (c279), passes p91 (c273), accurate-passes-percentage p80 (c240) |
| 3 | Douglas Luiz | Nottingham Forest | 85.7 | 930 | passes p93 (c279), accurate-passes-percentage p92 (c276), key-passes p87 (c261) |
| 4 | Declan Rice | Arsenal | 83.6 | 3099 | passes p92 (c276), key-passes p88 (c264), accurate-passes-percentage p77 (c231) |
| 5 | Curtis Jones | Liverpool | 81.3 | 1930 | accurate-passes-percentage p99 (c297), passes p99 (c297), key-passes p49 (c147) |
| 6 | Bernardo Silva | Manchester City | 81.0 | 2888 | passes p97 (c291), accurate-passes-percentage p95 (c285), key-passes p72 (c216) |
| 7 | Enzo Fernández | Chelsea | 80.3 | 3121 | key-passes p91 (c273), passes p89 (c267), accurate-passes-percentage p65 (c195) |
| 8 | Elliot Anderson | Nottingham Forest | 78.5 | 3334 | passes p94 (c282), key-passes p76 (c228), accurate-passes-percentage p58 (c174) |
| 9 | James Ward-Prowse | Burnley | 78.3 | 1097 | key-passes p89 (c267), accurate-passes-percentage p83 (c249), passes p68 (c204) |
| 10 | Phil Foden | Manchester City | 78.0 | 2086 | key-passes p96 (c288), accurate-passes-percentage p81 (c243), passes p74 (c222) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Keane Lewis-Potter | Brentford | 22.3 | 1979 | key-passes p35 (c105), long-balls p69 (c104), long-balls-won p27 (c40) |
| 2 | Brenden Aaronson | Leeds United | 22.0 | 2479 | key-passes p58 (c174), accurate-passes-percentage p20 (c60), through-balls p60 (c30) |
| 3 | Mateus Mané | Wolverhampton Wanderers | 21.9 | 1791 | key-passes p79 (c237), long-balls p13 (c20), long-balls-won p7 (c10) |
| 4 | Tomáš Souček | West Ham United | 20.5 | 2198 | long-balls p52 (c78), passes p24 (c72), long-balls-won p40 (c60) |
| 5 | Diego Gómez | Brighton & Hove Albion | 18.4 | 2138 | key-passes p38 (c114), passes p12 (c36), accurate-passes-percentage p10 (c30) |
| 6 | Lesley Ugochukwu | Burnley | 16.8 | 2350 | accurate-passes-percentage p37 (c111), long-balls-won p20 (c30), long-balls p16 (c24) |
| 7 | Josh King | Fulham | 16.7 | 1304 | key-passes p50 (c150), accurate-passes-percentage p16 (c48), through-balls p32 (c16) |
| 8 | Tim Iroegbunam | Everton | 15.4 | 1487 | accurate-passes-percentage p26 (c78), interceptions p82 (c41), key-passes p10 (c30) |
| 9 | Lucas Bergvall | Tottenham Hotspur | 15.3 | 974 | accurate-passes-percentage p28 (c84), through-balls p62 (c31), long-balls-won p18 (c27) |
| 10 | Habib Diarra | Sunderland | 11.3 | 1408 | accurate-passes-percentage p29 (c87), through-balls p48 (c24), key-passes p5 (c15) |

### Serie A 2025/2026

n = 111 · media 49.9 · mediana 50.6 · desv 20.3 · rango [6.1, 93.5]

```
    0-10  | ### 2
   10-20  | ######### 7
   20-30  | ################# 13
   30-40  | ################# 13
   40-50  | ########################### 20
   50-60  | ######################## 18
   60-70  | ############################ 21
   70-80  | ############### 11
   80-90  | ##### 4
   90-100 | ### 2
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Hakan Çalhanoğlu | Inter | 93.5 | 1651 | passes p99 (c297), accurate-passes-percentage p95 (c284), key-passes p95 (c284) |
| 2 | Luka Modrić | AC Milan | 93.0 | 2816 | passes p97 (c292), accurate-passes-percentage p93 (c278), key-passes p88 (c265) |
| 3 | Manuel Locatelli | Juventus | 88.5 | 3006 | passes p100 (c300), accurate-passes-percentage p79 (c237), key-passes p76 (c229) |
| 4 | Nicolò Fagioli | Fiorentina | 88.0 | 2567 | key-passes p94 (c281), accurate-passes-percentage p90 (c270), passes p88 (c265) |
| 5 | Mario Pašalić | Atalanta | 87.1 | 1932 | passes p94 (c281), key-passes p91 (c273), accurate-passes-percentage p82 (c245) |
| 6 | Nicolò Barella | Inter | 81.4 | 2534 | key-passes p97 (c292), passes p91 (c273), accurate-passes-percentage p66 (c199) |
| 7 | Petar Sučić | Inter | 79.5 | 1794 | accurate-passes-percentage p88 (c265), passes p84 (c251), key-passes p77 (c232) |
| 8 | Nikola Moro | Bologna | 79.2 | 1798 | passes p95 (c286), key-passes p67 (c202), accurate-passes-percentage p59 (c177) |
| 9 | Lucas Da Cunha | Como | 78.5 | 2747 | passes p93 (c278), accurate-passes-percentage p92 (c275), key-passes p80 (c240) |
| 10 | Máximo Perrone | Como | 78.0 | 2751 | passes p98 (c295), accurate-passes-percentage p96 (c289), key-passes p55 (c164) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Oliver Sørensen | Parma | 20.7 | 1835 | accurate-passes-percentage p45 (c136), interceptions p57 (c29), long-balls p18 (c27) |
| 2 | Martín Payero | Cremonese | 18.6 | 1459 | key-passes p25 (c74), long-balls p32 (c48), passes p13 (c38) |
| 3 | Giovanni Fabbian | Bologna | 16.4 | 1188 | accurate-passes-percentage p26 (c79), key-passes p22 (c65), long-balls-won p17 (c26) |
| 4 | Christian Ordóñez | Parma | 15.8 | 1086 | accurate-passes-percentage p38 (c115), key-passes p9 (c27), through-balls p49 (c25) |
| 5 | Michael Folorunsho | Cagliari | 15.3 | 2009 | key-passes p20 (c60), long-balls p34 (c50), long-balls-won p23 (c34) |
| 6 | Jens Odgaard | Bologna | 14.2 | 1381 | key-passes p40 (c120), accurate-passes-percentage p7 (c22), through-balls p42 (c21) |
| 7 | Jean-Daniel Akpa Akpro | Hellas Verona | 12.8 | 1511 | key-passes p19 (c57), interceptions p92 (c46), accurate-passes-percentage p9 (c27) |
| 8 | Morten Thorsby | Cremonese | 11.3 | 1376 | key-passes p14 (c41), passes p14 (c41), through-balls p43 (c21) |
| 9 | Mikael Egill Ellertsson | Genoa | 8.2 | 2768 | accurate-passes-percentage p12 (c35), key-passes p10 (c30), long-balls p13 (c19) |
| 10 | Omri Gandelman | Lecce | 6.1 | 975 | key-passes p17 (c52), passes p5 (c16), interceptions p19 (c10) |

### Bundesliga 2025/2026

n = 84 · media 50.0 · mediana 49.5 · desv 18.7 · rango [6.5, 96.4]

```
    0-10  | # 1
   10-20  | #### 3
   20-30  | ############# 10
   30-40  | ############ 9
   40-50  | ############################ 21
   50-60  | ######################## 18
   60-70  | ############ 9
   70-80  | ########### 8
   80-90  | #### 3
   90-100 | ### 2
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Joshua Kimmich | FC Bayern München | 96.4 | 2280 | passes p100 (c300), accurate-passes-percentage p96 (c289), key-passes p95 (c286) |
| 2 | Aleix García | Bayer 04 Leverkusen | 92.1 | 2677 | passes p99 (c296), accurate-passes-percentage p99 (c296), key-passes p86 (c257) |
| 3 | Angelo Stiller | VfB Stuttgart | 87.3 | 2746 | passes p94 (c282), key-passes p90 (c271), accurate-passes-percentage p84 (c253) |
| 4 | Aleksandar Pavlovic | FC Bayern München | 83.6 | 1462 | accurate-passes-percentage p100 (c300), passes p98 (c293), key-passes p63 (c188) |
| 5 | Tom Bischof | FC Bayern München | 81.6 | 1296 | accurate-passes-percentage p98 (c293), passes p95 (c286), key-passes p80 (c239) |
| 6 | Leon Goretzka | FC Bayern München | 76.5 | 1961 | accurate-passes-percentage p95 (c286), passes p92 (c275), key-passes p51 (c152) |
| 7 | Ezequiel Fernández | Bayer 04 Leverkusen | 75.3 | 995 | passes p93 (c278), accurate-passes-percentage p89 (c267), long-balls-won p94 (c141) |
| 8 | Kevin Stöger | Borussia Mönchengladbach | 74.6 | 1323 | key-passes p89 (c267), passes p86 (c257), accurate-passes-percentage p48 (c145) |
| 9 | Nadiem Amiri | FSV Mainz 05 | 73.8 | 2092 | key-passes p100 (c300), passes p66 (c199), long-balls p94 (c141) |
| 10 | Maximilian Arnold | VfL Wolfsburg | 72.4 | 1854 | passes p73 (c220), key-passes p69 (c206), accurate-passes-percentage p61 (c184) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | James Sands | St. Pauli | 26.2 | 1941 | passes p43 (c130), long-balls p54 (c81), interceptions p95 (c48) |
| 2 | Robin Fellhauer | FC Augsburg | 26.0 | 2808 | key-passes p49 (c148), long-balls p31 (c47), long-balls-won p30 (c45) |
| 3 | Jae-sung Lee | FSV Mainz 05 | 24.9 | 2201 | key-passes p43 (c130), accurate-passes-percentage p22 (c65), through-balls p71 (c36) |
| 4 | Jens Castrop | Borussia Mönchengladbach | 24.7 | 1595 | key-passes p57 (c170), long-balls p23 (c34), long-balls-won p20 (c31) |
| 5 | Anton Kade | FC Augsburg | 21.4 | 1745 | key-passes p67 (c202), through-balls p51 (c25), interceptions p27 (c13) |
| 6 | András Schäfer | FC Union Berlin | 20.3 | 1427 | key-passes p22 (c65), accurate-passes-percentage p18 (c54), passes p16 (c47) |
| 7 | Jan Schöppner | FC Heidenheim | 19.7 | 2264 | long-balls p48 (c72), key-passes p19 (c58), interceptions p81 (c40) |
| 8 | Bakery Jatta | Hamburger SV | 15.9 | 918 | accurate-passes-percentage p40 (c119), long-balls-won p24 (c36), interceptions p55 (c28) |
| 9 | Rani Khedira | FC Union Berlin | 11.2 | 2835 | key-passes p17 (c51), long-balls p25 (c38), interceptions p70 (c35) |
| 10 | Woo-yeong Jeong | FC Union Berlin | 6.5 | 1192 | accurate-passes-percentage p11 (c33), key-passes p7 (c22), interceptions p22 (c11) |


---

## Advanced Playmaker

### La Liga 2024/2025

n = 149 · media 49.4 · mediana 50.5 · desv 22.2 · rango [3.4, 97.4]

```
    0-10  | ##### 6
   10-20  | ###### 8
   20-30  | ############### 19
   30-40  | ############### 19
   40-50  | ################ 20
   50-60  | ############################ 35
   60-70  | ########## 13
   70-80  | ########## 12
   80-90  | ######### 11
   90-100 | ##### 6
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Isco | Real Betis | 97.4 | 1550 | assists p100 (c300), key-passes p100 (c300), big-chances-created p96 (c287) |
| 2 | Arda Güler | Real Madrid | 95.2 | 1248 | big-chances-created p99 (c297), key-passes p98 (c294), assists p93 (c278) |
| 3 | Lamine Yamal | FC Barcelona | 94.0 | 2864 | assists p100 (c300), key-passes p88 (c265), big-chances-created p87 (c260) |
| 4 | Dani Olmo | FC Barcelona | 93.7 | 1214 | assists p96 (c287), big-chances-created p92 (c275), key-passes p92 (c275) |
| 5 | Giovani Lo Celso | Real Betis | 92.2 | 1454 | big-chances-created p98 (c294), key-passes p97 (c291), assists p84 (c253) |
| 6 | Fermín López | FC Barcelona | 91.2 | 1256 | assists p99 (c297), key-passes p93 (c278), big-chances-created p75 (c224) |
| 7 | Edu Expósito | Espanyol | 88.7 | 1045 | key-passes p96 (c287), big-chances-created p89 (c268), assists p81 (c243) |
| 8 | Vinicius Junior | Real Madrid | 87.2 | 2259 | key-passes p92 (c277), assists p90 (c271), big-chances-created p69 (c208) |
| 9 | Raphinha | FC Barcelona | 86.6 | 2845 | key-passes p98 (c294), assists p96 (c288), big-chances-created p96 (c288) |
| 10 | Luka Modrić | Real Madrid | 86.4 | 1817 | big-chances-created p100 (c300), key-passes p99 (c297), assists p97 (c291) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Óscar Valentín | Rayo Vallecano | 14.9 | 1830 | key-passes p28 (c85), big-chances-created p26 (c79), dribble-attempts p8 (c13) |
| 2 | Arthur Melo | Girona | 14.7 | 942 | successful-dribbles p63 (c95), dribble-attempts p36 (c54), key-passes p12 (c35) |
| 3 | Oriol Romeu | Girona | 14.1 | 1361 | big-chances-created p19 (c57), key-passes p18 (c54), through-balls p62 (c31) |
| 4 | Juanmi | Real Betis | 11.3 | 939 | big-chances-created p17 (c52), successful-dribbles p23 (c35), key-passes p12 (c35) |
| 5 | Takuma Asano | Mallorca | 9.9 | 1058 | assists p23 (c69), dribble-attempts p19 (c29), successful-dribbles p10 (c14) |
| 6 | Omar Mascarell | Mallorca | 7.6 | 1991 | big-chances-created p11 (c32), successful-dribbles p17 (c25), dribble-attempts p17 (c25) |
| 7 | Stanko Juric | Real Valladolid | 5.4 | 1738 | successful-dribbles p14 (c21), dribble-attempts p14 (c21), through-balls p27 (c14) |
| 8 | Lucas Torró | Osasuna | 3.9 | 2966 | big-chances-created p8 (c25), key-passes p5 (c16), successful-dribbles p4 (c6) |
| 9 | Anuar | Real Valladolid | 3.7 | 1728 | big-chances-created p8 (c23), through-balls p29 (c14), dribble-attempts p4 (c6) |
| 10 | Aurélien Tchouaméni | Real Madrid | 3.4 | 2692 | successful-dribbles p13 (c19), big-chances-created p4 (c13), dribble-attempts p5 (c8) |

### La Liga 2025/2026

n = 150 · media 49.3 · mediana 49.5 · desv 23.2 · rango [1.7, 99.7]

```
    0-10  | ###### 5
   10-20  | ############## 11
   20-30  | ####################### 18
   30-40  | ############################ 22
   40-50  | ######################### 20
   50-60  | ############################ 22
   60-70  | ################### 15
   70-80  | ############################ 22
   80-90  | ############## 11
   90-100 | ##### 4
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Lamine Yamal | FC Barcelona | 99.7 | 2296 | big-chances-created p100 (c300), assists p100 (c300), key-passes p100 (c300) |
| 2 | Fermín López | FC Barcelona | 94.1 | 1798 | big-chances-created p100 (c300), assists p100 (c300), key-passes p77 (c232) |
| 3 | Arda Güler | Real Madrid | 93.2 | 2028 | key-passes p100 (c300), assists p99 (c297), big-chances-created p99 (c297) |
| 4 | Pedri | FC Barcelona | 91.8 | 2111 | assists p98 (c294), key-passes p97 (c290), big-chances-created p84 (c252) |
| 5 | Ander Barrenetxea | Real Sociedad | 89.2 | 1772 | key-passes p93 (c278), big-chances-created p93 (c278), assists p84 (c251) |
| 6 | Dani Olmo | FC Barcelona | 87.7 | 2074 | big-chances-created p97 (c290), assists p97 (c290), key-passes p94 (c281) |
| 7 | Edu Expósito | Espanyol | 86.6 | 2542 | key-passes p99 (c297), big-chances-created p94 (c281), assists p84 (c252) |
| 8 | Azzedine Ounahi | Girona | 86.3 | 1766 | big-chances-created p98 (c294), key-passes p84 (c252), assists p61 (c184) |
| 9 | Nicolas Pépé | Villarreal | 85.3 | 2398 | assists p89 (c267), key-passes p87 (c262), big-chances-created p84 (c251) |
| 10 | Brahim Díaz | Real Madrid | 84.9 | 1253 | assists p98 (c295), key-passes p89 (c267), big-chances-created p85 (c256) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Batista Mendy | Sevilla | 14.9 | 1620 | successful-dribbles p46 (c69), dribble-attempts p35 (c53), key-passes p14 (c42) |
| 2 | Oriol Rey | Levante | 14.7 | 1318 | assists p38 (c113), key-passes p23 (c68), dribble-attempts p1 (c2) |
| 3 | Iker Muñoz | Osasuna | 11.7 | 947 | dribble-attempts p42 (c63), successful-dribbles p22 (c32), key-passes p11 (c32) |
| 4 | Óscar Valentín | Rayo Vallecano | 11.5 | 2118 | big-chances-created p23 (c68), dribble-attempts p19 (c29), key-passes p9 (c26) |
| 5 | Nemanja Gudelj | Sevilla | 10.9 | 2347 | big-chances-created p32 (c97), dribble-attempts p10 (c15), successful-dribbles p6 (c10) |
| 6 | Sofyan Amrabat | Real Betis | 9.0 | 1295 | successful-dribbles p32 (c48), key-passes p13 (c39), dribble-attempts p17 (c26) |
| 7 | Leander Dendoncker | Real Oviedo | 7.1 | 1333 | dribble-attempts p20 (c31), key-passes p10 (c29), successful-dribbles p19 (c29) |
| 8 | Adrián Liso | Getafe | 4.6 | 1714 | dribble-attempts p25 (c38), successful-dribbles p13 (c19), key-passes p0 (c0) |
| 9 | Nicolás Fonseca | Real Oviedo | 2.9 | 1021 | through-balls p33 (c17), dribble-attempts p6 (c10), successful-dribbles p4 (c6) |
| 10 | Kwasi Sibo | Real Oviedo | 1.7 | 1688 | successful-dribbles p12 (c18), dribble-attempts p2 (c3), through-balls p0 (c0) |

### La Liga 2 2025/2026

n = 171 · media 47.5 · mediana 47.7 · desv 22.4 · rango [1.9, 94.1]

```
    0-10  | ######## 8
   10-20  | ############# 13
   20-30  | ####################### 22
   30-40  | ############################ 27
   40-50  | ######################### 24
   50-60  | ######################## 23
   60-70  | ######################### 24
   70-80  | ############### 14
   80-90  | ############### 14
   90-100 | ## 2
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Israel Suero | Castellón | 94.1 | 1114 | key-passes p100 (c300), big-chances-created p100 (c300), assists p100 (c300) |
| 2 | Álex Calatrava | Castellón | 92.0 | 3672 | key-passes p99 (c297), big-chances-created p97 (c291), assists p89 (c266) |
| 3 | Dani Rodríguez | Leganés | 89.1 | 1201 | assists p98 (c294), big-chances-created p96 (c287), key-passes p95 (c284) |
| 4 | Dalisson de Almeida | Córdoba | 88.0 | 1133 | key-passes p98 (c294), big-chances-created p93 (c278), assists p80 (c241) |
| 5 | Javi Hernández | Mirandés | 87.6 | 1861 | big-chances-created p99 (c297), key-passes p90 (c269), assists p77 (c231) |
| 6 | Nico Melamed | Almería | 86.9 | 1114 | assists p93 (c278), key-passes p91 (c272), big-chances-created p88 (c262) |
| 7 | Yeray Cabanzón | FC Andorra | 86.6 | 1033 | big-chances-created p99 (c296), assists p96 (c288), key-passes p95 (c284) |
| 8 | Chuki | Real Valladolid | 86.5 | 2339 | big-chances-created p98 (c294), assists p95 (c284), key-passes p85 (c256) |
| 9 | Brian Cipenga | Castellón | 85.6 | 2249 | assists p97 (c292), key-passes p86 (c259), big-chances-created p81 (c242) |
| 10 | Sergio Arribas | Almería | 84.0 | 3812 | key-passes p97 (c291), assists p82 (c247), big-chances-created p80 (c241) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Gui Guedes | Almería | 11.4 | 1237 | successful-dribbles p41 (c61), dribble-attempts p35 (c53), key-passes p9 (c28) |
| 2 | Anuar | Ceuta | 10.4 | 1935 | assists p36 (c107), big-chances-created p5 (c16), key-passes p1 (c4) |
| 3 | Moussa Diakité | Cádiz | 9.6 | 2719 | successful-dribbles p26 (c39), big-chances-created p12 (c38), dribble-attempts p25 (c38) |
| 4 | Diego Villares | Deportivo A Coruña | 9.5 | 2460 | key-passes p15 (c44), dribble-attempts p26 (c39), successful-dribbles p24 (c36) |
| 5 | Jesús Álvarez | Huesca | 9.4 | 2631 | successful-dribbles p44 (c66), dribble-attempts p28 (c42), key-passes p3 (c9) |
| 6 | Ale García | Las Palmas | 8.2 | 2166 | assists p29 (c86), successful-dribbles p7 (c10), dribble-attempts p4 (c6) |
| 7 | Valery Fernández | Real Zaragoza | 7.4 | 977 | successful-dribbles p34 (c51), dribble-attempts p11 (c16), key-passes p4 (c12) |
| 8 | Javi Mier | Huesca | 7.1 | 916 | dribble-attempts p27 (c41), key-passes p12 (c38), successful-dribbles p7 (c11) |
| 9 | Sergi Maestre | Cultural Leonesa | 2.6 | 1112 | key-passes p7 (c22), dribble-attempts p4 (c6), successful-dribbles p3 (c5) |
| 10 | Miguel Atienza | Burgos | 1.9 | 3516 | dribble-attempts p9 (c14), successful-dribbles p6 (c9), through-balls p0 (c0) |

### Premier League 2025/2026

n = 153 · media 49.7 · mediana 50.0 · desv 21.9 · rango [2.8, 99.3]

```
    0-10  | #### 4
   10-20  | ########### 13
   20-30  | ########### 13
   30-40  | #################### 23
   40-50  | ##################### 24
   50-60  | ############### 17
   60-70  | ############################ 32
   70-80  | ############## 16
   80-90  | ####### 8
   90-100 | ### 3
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Rayan Cherki | Manchester City | 99.3 | 1785 | key-passes p99 (c297), big-chances-created p99 (c297), assists p99 (c297) |
| 2 | Jérémy Doku | Manchester City | 93.1 | 1786 | key-passes p100 (c300), big-chances-created p92 (c276), assists p80 (c241) |
| 3 | Phil Foden | Manchester City | 90.6 | 2086 | big-chances-created p96 (c288), key-passes p96 (c288), assists p90 (c270) |
| 4 | Xavi Simons | Tottenham Hotspur | 89.7 | 1756 | assists p93 (c279), big-chances-created p89 (c267), key-passes p84 (c252) |
| 5 | Hannibal | Burnley | 86.8 | 1238 | assists p97 (c291), big-chances-created p82 (c246), key-passes p80 (c240) |
| 6 | Martin Ødegaard | Arsenal | 86.4 | 1370 | key-passes p98 (c294), assists p98 (c294), big-chances-created p87 (c261) |
| 7 | Bruno Fernandes | Manchester United | 84.7 | 3069 | key-passes p100 (c300), big-chances-created p100 (c300), assists p100 (c300) |
| 8 | Mikkel Damsgaard | Brentford | 83.4 | 2059 | big-chances-created p97 (c291), key-passes p86 (c258), assists p76 (c228) |
| 9 | Bukayo Saka | Arsenal | 82.3 | 2226 | key-passes p98 (c294), big-chances-created p84 (c253), assists p76 (c229) |
| 10 | Omari Hutchinson | Nottingham Forest | 81.5 | 1682 | big-chances-created p88 (c265), assists p84 (c253), key-passes p75 (c224) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Andrey Santos | Chelsea | 13.8 | 1255 | big-chances-created p22 (c66), key-passes p18 (c54), through-balls p71 (c36) |
| 2 | Loum Tchaouna | Burnley | 13.4 | 1278 | assists p22 (c65), big-chances-created p12 (c35), through-balls p47 (c24) |
| 3 | Chemsdine Talbi | Sunderland | 12.2 | 1563 | successful-dribbles p33 (c50), assists p14 (c41), dribble-attempts p22 (c32) |
| 4 | Brennan Johnson | Crystal Palace | 11.5 | 1729 | key-passes p27 (c82), assists p8 (c24), through-balls p29 (c15) |
| 5 | Amadou Onana | Aston Villa | 11.3 | 1778 | big-chances-created p15 (c45), successful-dribbles p25 (c38), through-balls p55 (c28) |
| 6 | Jhon Arias | Wolverhampton Wanderers | 10.1 | 1127 | big-chances-created p20 (c59), key-passes p10 (c29), successful-dribbles p14 (c21) |
| 7 | Rodrigo Gomes | Wolverhampton Wanderers | 6.3 | 961 | dribble-attempts p29 (c44), successful-dribbles p24 (c35), key-passes p0 (c0) |
| 8 | Ismaïla Sarr | Crystal Palace | 5.7 | 2177 | big-chances-created p8 (c24), key-passes p6 (c18), through-balls p25 (c13) |
| 9 | Tomáš Souček | West Ham United | 5.5 | 2198 | big-chances-created p11 (c33), key-passes p6 (c18), successful-dribbles p8 (c12) |
| 10 | Lamare Bogarde | Aston Villa | 2.8 | 1048 | dribble-attempts p17 (c26), successful-dribbles p6 (c9), key-passes p0 (c0) |

### Serie A 2025/2026

n = 140 · media 49.3 · mediana 48.7 · desv 22.8 · rango [4.2, 97.1]

```
    0-10  | #### 4
   10-20  | ########### 11
   20-30  | ###################### 22
   30-40  | ############# 13
   40-50  | ###################### 22
   50-60  | ############## 14
   60-70  | ############################ 28
   70-80  | ############## 14
   80-90  | ##### 5
   90-100 | ####### 7
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Cristian Volpato | Sassuolo | 97.1 | 1062 | assists p99 (c297), big-chances-created p97 (c292), key-passes p93 (c278) |
| 2 | Charles De Ketelaere | Atalanta | 96.7 | 2189 | big-chances-created p100 (c300), key-passes p98 (c295), assists p92 (c275) |
| 3 | Nicola Zalewski | Atalanta | 93.1 | 1905 | big-chances-created p99 (c297), assists p90 (c270), key-passes p89 (c267) |
| 4 | Nicolò Barella | Inter | 93.1 | 2534 | assists p98 (c295), key-passes p97 (c292), big-chances-created p95 (c284) |
| 5 | Nico Paz | Como | 90.8 | 2887 | big-chances-created p92 (c275), assists p88 (c265), key-passes p85 (c254) |
| 6 | Martin Baturina | Como | 90.6 | 1591 | key-passes p100 (c300), big-chances-created p94 (c281), assists p83 (c248) |
| 7 | Jesús Rodríguez | Como | 90.3 | 1733 | assists p100 (c300), big-chances-created p96 (c289), key-passes p82 (c246) |
| 8 | David Neres | Napoli | 87.0 | 925 | big-chances-created p100 (c300), assists p93 (c279), key-passes p86 (c257) |
| 9 | Kenan Yıldız | Juventus | 84.9 | 2844 | key-passes p100 (c300), big-chances-created p82 (c246), assists p64 (c193) |
| 10 | Maxence Caqueret | Como | 82.8 | 1488 | assists p100 (c300), key-passes p84 (c251), big-chances-created p58 (c175) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Ylber Ramadani | Lecce | 14.4 | 3215 | successful-dribbles p29 (c44), dribble-attempts p25 (c38), big-chances-created p12 (c35) |
| 2 | Cher Ndour | Fiorentina | 14.3 | 1873 | dribble-attempts p45 (c67), big-chances-created p18 (c55), successful-dribbles p23 (c34) |
| 3 | Christian Ordóñez | Parma | 14.1 | 1086 | dribble-attempts p51 (c76), successful-dribbles p32 (c48), key-passes p9 (c27) |
| 4 | Teun Koopmeiners | Juventus | 12.6 | 1819 | key-passes p35 (c104), successful-dribbles p13 (c19), through-balls p35 (c18) |
| 5 | Morten Frendrup | Genoa | 10.3 | 3089 | big-chances-created p23 (c68), successful-dribbles p14 (c20), key-passes p5 (c14) |
| 6 | Alberto Grassi | Cremonese | 10.1 | 1755 | successful-dribbles p31 (c46), through-balls p81 (c40), key-passes p7 (c22) |
| 7 | Jesper Karlström | Udinese | 8.4 | 3153 | big-chances-created p13 (c38), dribble-attempts p16 (c25), successful-dribbles p15 (c23) |
| 8 | Roberto Gagliardini | Hellas Verona | 8.1 | 2213 | key-passes p18 (c55), successful-dribbles p12 (c18), through-balls p33 (c16) |
| 9 | Adrien Tamèze | Torino | 4.5 | 1138 | key-passes p15 (c46), dribble-attempts p6 (c10), through-balls p0 (c0) |
| 10 | Marius Marin | Pisa | 4.2 | 1290 | through-balls p67 (c34), dribble-attempts p10 (c15), successful-dribbles p3 (c4) |

### Bundesliga 2025/2026

n = 118 · media 49.6 · mediana 46.7 · desv 23.5 · rango [2.0, 97.1]

```
    0-10  | ##### 4
   10-20  | ############## 11
   20-30  | ################# 13
   30-40  | ################# 13
   40-50  | ############################ 22
   50-60  | ############## 11
   60-70  | ################### 15
   70-80  | ################# 13
   80-90  | ################## 14
   90-100 | ### 2
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Michael Olise | FC Bayern München | 97.1 | 2315 | key-passes p100 (c300), big-chances-created p100 (c300), assists p100 (c300) |
| 2 | Romano Schmid | Werder Bremen | 92.6 | 2993 | key-passes p99 (c296), big-chances-created p95 (c286), assists p88 (c264) |
| 3 | Can Uzun | Eintracht Frankfurt | 88.2 | 1163 | assists p100 (c300), big-chances-created p83 (c249), key-passes p77 (c231) |
| 4 | Luis Díaz | FC Bayern München | 87.9 | 2480 | assists p97 (c291), key-passes p91 (c273), big-chances-created p82 (c245) |
| 5 | Bilal El Khannouss | VfB Stuttgart | 87.8 | 1636 | key-passes p98 (c293), assists p92 (c275), big-chances-created p88 (c264) |
| 6 | Julian Brandt | Borussia Dortmund | 86.2 | 1606 | big-chances-created p90 (c271), key-passes p88 (c264), assists p87 (c260) |
| 7 | Lennart Karl | FC Bayern München | 84.5 | 1283 | assists p98 (c293), key-passes p81 (c242), big-chances-created p64 (c192) |
| 8 | Chris Führich | VfB Stuttgart | 84.2 | 1705 | big-chances-created p97 (c291), key-passes p97 (c291), assists p94 (c282) |
| 9 | Yan Diomande | RB Leipzig | 84.2 | 2484 | big-chances-created p91 (c273), assists p79 (c236), key-passes p76 (c227) |
| 10 | Farès Chaïbi | Eintracht Frankfurt | 83.7 | 1798 | assists p99 (c296), key-passes p93 (c278), big-chances-created p93 (c278) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Eren Dinkçi | SC Freiburg | 15.3 | 1382 | assists p33 (c100), dribble-attempts p18 (c27), through-balls p45 (c23) |
| 2 | Yannick Gerhardt | VfL Wolfsburg | 15.2 | 1071 | key-passes p28 (c83), big-chances-created p22 (c65), dribble-attempts p27 (c40) |
| 3 | Ellyes Skhiri | Eintracht Frankfurt | 11.6 | 1442 | successful-dribbles p36 (c54), dribble-attempts p31 (c47), key-passes p14 (c43) |
| 4 | Justin Njinmah | Werder Bremen | 11.3 | 1953 | dribble-attempts p45 (c68), successful-dribbles p42 (c64), key-passes p3 (c9) |
| 5 | Vinicius de Souza Costa | VfL Wolfsburg | 11.0 | 1773 | successful-dribbles p31 (c47), dribble-attempts p29 (c43), big-chances-created p13 (c40) |
| 6 | Senne Lynen | Werder Bremen | 10.5 | 2757 | key-passes p12 (c36), dribble-attempts p23 (c34), big-chances-created p10 (c29) |
| 7 | James Sands | St. Pauli | 9.5 | 1941 | big-chances-created p24 (c72), key-passes p11 (c33), successful-dribbles p6 (c9) |
| 8 | Jan Thielmann | FC Köln | 9.0 | 1551 | assists p15 (c45), dribble-attempts p12 (c18), key-passes p6 (c18) |
| 9 | Philipp Sander | Borussia Mönchengladbach | 4.5 | 2456 | dribble-attempts p13 (c20), through-balls p37 (c19), successful-dribbles p10 (c14) |
| 10 | Robert Andrich | Bayer 04 Leverkusen | 2.0 | 2548 | key-passes p5 (c14), through-balls p18 (c9), dribble-attempts p1 (c2) |


---

## Central Constructor

### La Liga 2024/2025

n = 63 · media 50.0 · mediana 48.2 · desv 18.5 · rango [11.2, 86.5]

```
    0-10  |  0
   10-20  | #### 2
   20-30  | ############## 7
   30-40  | ###################### 11
   40-50  | ############################ 14
   50-60  | ################## 9
   60-70  | ################## 9
   70-80  | ############## 7
   80-90  | ######## 4
   90-100 |  0
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Iñigo Martínez | FC Barcelona | 86.5 | 2493 | long-balls-won p100 (c300), accurate-passes-percentage p89 (c266), long-balls p76 (c227) |
| 2 | Daley Blind | Girona | 83.4 | 2778 | long-balls-won p97 (c290), accurate-passes-percentage p79 (c237), long-balls p73 (c218) |
| 3 | Éder Militão | Real Madrid | 81.3 | 939 | long-balls-won p90 (c271), accurate-passes-percentage p77 (c232), long-balls p77 (c232) |
| 4 | Clément Lenglet | Atlético de Madrid | 80.2 | 1976 | long-balls-won p92 (c276), long-balls p90 (c271), accurate-passes-percentage p61 (c184) |
| 5 | Nayef Aguerd | Real Sociedad | 79.8 | 1764 | long-balls-won p95 (c285), long-balls p92 (c276), accurate-passes-percentage p60 (c179) |
| 6 | Antonio Rüdiger | Real Madrid | 79.2 | 2290 | accurate-passes-percentage p92 (c276), long-balls-won p89 (c266), long-balls p66 (c198) |
| 7 | José María Giménez | Atlético de Madrid | 77.9 | 1993 | accurate-passes-percentage p90 (c271), long-balls-won p87 (c261), long-balls p56 (c169) |
| 8 | Marcos Alonso | Celta de Vigo | 74.5 | 2649 | accurate-passes-percentage p84 (c252), long-balls-won p74 (c223), long-balls p58 (c174) |
| 9 | Dani Vivian | Athletic Club | 73.9 | 2604 | long-balls-won p82 (c247), long-balls p79 (c237), accurate-passes-percentage p56 (c169) |
| 10 | Florian Lejeune | Rayo Vallecano | 72.2 | 3326 | long-balls p98 (c295), long-balls-won p98 (c295), passes p65 (c97) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Scott McKenna | Las Palmas | 31.4 | 2467 | accurate-passes-percentage p52 (c155), passes p53 (c80), long-balls p23 (c68) |
| 2 | Enzo Boyomo | Osasuna | 28.1 | 3257 | accurate-passes-percentage p55 (c165), long-balls p18 (c53), interceptions p73 (c36) |
| 3 | Jorge Herrando | Osasuna | 26.5 | 1376 | accurate-passes-percentage p40 (c121), long-balls p24 (c73), passes p35 (c53) |
| 4 | David Torres | Real Valladolid | 26.4 | 1386 | long-balls p39 (c116), long-balls-won p26 (c77), accurate-passes-percentage p18 (c53) |
| 5 | Juanma Herzog | Las Palmas | 25.3 | 1313 | accurate-passes-percentage p53 (c160), interceptions p92 (c46), long-balls p10 (c29) |
| 6 | Gerard Martín | FC Barcelona | 23.1 | 1030 | accurate-passes-percentage p37 (c111), passes p68 (c102), interceptions p82 (c41) |
| 7 | Juan Berrocal | Getafe | 22.0 | 1071 | long-balls p44 (c131), long-balls-won p21 (c63), interceptions p77 (c39) |
| 8 | Matija Nastasić | Leganés | 21.3 | 2111 | long-balls p31 (c92), long-balls-won p19 (c58), accurate-passes-percentage p16 (c48) |
| 9 | Moussa Diarra | Deportivo Alavés | 14.3 | 1862 | accurate-passes-percentage p23 (c68), long-balls p13 (c39), long-balls-won p8 (c24) |
| 10 | Dakonam Djené | Getafe | 11.2 | 2555 | long-balls-won p16 (c48), long-balls p15 (c44), accurate-passes-percentage p6 (c19) |

### La Liga 2025/2026

n = 69 · media 50.0 · mediana 49.5 · desv 17.1 · rango [10.9, 85.2]

```
    0-10  |  0
   10-20  | ##### 3
   20-30  | ########## 6
   30-40  | ################### 11
   40-50  | ############################ 16
   50-60  | ################### 11
   60-70  | ######################## 14
   70-80  | ####### 4
   80-90  | ####### 4
   90-100 |  0
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Daley Blind | Girona | 85.2 | 2610 | long-balls-won p94 (c282), long-balls p91 (c274), accurate-passes-percentage p68 (c203) |
| 2 | Marcos Alonso | Celta de Vigo | 84.8 | 2770 | long-balls-won p93 (c278), long-balls p88 (c265), accurate-passes-percentage p76 (c229) |
| 3 | Dean Huijsen | Real Madrid | 82.4 | 2038 | long-balls-won p96 (c287), long-balls p84 (c251), accurate-passes-percentage p72 (c216) |
| 4 | Clément Lenglet | Atlético de Madrid | 81.2 | 1394 | long-balls-won p100 (c300), long-balls p97 (c291), accurate-passes-percentage p49 (c146) |
| 5 | Pedro Bigas | Elche | 77.8 | 2070 | long-balls-won p84 (c251), long-balls p81 (c243), accurate-passes-percentage p63 (c190) |
| 6 | Florian Lejeune | Rayo Vallecano | 75.1 | 3231 | long-balls p96 (c287), long-balls-won p88 (c265), accurate-passes-percentage p41 (c124) |
| 7 | Éder Militão | Real Madrid | 74.1 | 1142 | accurate-passes-percentage p85 (c256), long-balls-won p81 (c243), long-balls p62 (c185) |
| 8 | José María Giménez | Atlético de Madrid | 70.5 | 1176 | long-balls-won p78 (c234), accurate-passes-percentage p74 (c221), long-balls p56 (c168) |
| 9 | David Costas | Real Oviedo | 67.7 | 2064 | long-balls-won p90 (c269), long-balls p75 (c225), accurate-passes-percentage p65 (c194) |
| 10 | Antonio Rüdiger | Real Madrid | 67.2 | 1491 | accurate-passes-percentage p96 (c287), long-balls-won p63 (c190), passes p90 (c135) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Dani Calvo | Real Oviedo | 30.0 | 1608 | accurate-passes-percentage p84 (c251), long-balls-won p10 (c31), passes p15 (c22) |
| 2 | Domingos Duarte | Getafe | 29.7 | 2930 | long-balls p50 (c150), long-balls-won p47 (c141), interceptions p49 (c24) |
| 3 | Enzo Boyomo | Osasuna | 29.4 | 2545 | long-balls p37 (c110), accurate-passes-percentage p34 (c101), long-balls-won p22 (c66) |
| 4 | Valentín Gómez | Real Betis | 29.1 | 1874 | long-balls p29 (c88), accurate-passes-percentage p28 (c84), long-balls-won p28 (c84) |
| 5 | Léo Pétrot | Elche | 27.3 | 1568 | accurate-passes-percentage p38 (c115), passes p65 (c97), long-balls-won p19 (c57) |
| 6 | Eric Bailly | Real Oviedo | 26.4 | 1236 | long-balls p41 (c124), long-balls-won p24 (c71), accurate-passes-percentage p18 (c53) |
| 7 | Pau Navarro | Villarreal | 24.3 | 1926 | accurate-passes-percentage p56 (c168), long-balls p12 (c35), passes p21 (c31) |
| 8 | Dakonam Djené | Getafe | 16.5 | 2586 | long-balls p28 (c84), long-balls-won p15 (c44), interceptions p72 (c36) |
| 9 | Jorge Herrando | Osasuna | 15.4 | 1598 | accurate-passes-percentage p29 (c88), interceptions p71 (c35), long-balls p9 (c26) |
| 10 | Unai Elgezabal | Levante | 10.9 | 960 | long-balls p19 (c57), accurate-passes-percentage p16 (c49), passes p6 (c9) |

### La Liga 2 2025/2026

n = 69 · media 50.0 · mediana 53.1 · desv 19.1 · rango [8.1, 87.9]

```
    0-10  | ## 1
   10-20  | ####### 4
   20-30  | ############# 8
   30-40  | ############ 7
   40-50  | ################## 11
   50-60  | ############################ 17
   60-70  | ################## 11
   70-80  | ########## 6
   80-90  | ####### 4
   90-100 |  0
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Jorge Sáenz | Leganés | 87.9 | 1031 | long-balls-won p99 (c296), long-balls p94 (c282), accurate-passes-percentage p74 (c221) |
| 2 | Diego Murillo | Málaga | 83.2 | 3429 | long-balls p97 (c291), long-balls-won p96 (c287), accurate-passes-percentage p53 (c159) |
| 3 | Álex Martín | Córdoba | 82.4 | 2402 | long-balls-won p90 (c269), accurate-passes-percentage p90 (c269), long-balls p75 (c225) |
| 4 | Anaitz Arbilla | SD Eibar | 80.3 | 2891 | long-balls-won p94 (c282), long-balls p88 (c265), accurate-passes-percentage p56 (c168) |
| 5 | Federico Bonini | Almería | 78.8 | 3464 | long-balls-won p87 (c260), accurate-passes-percentage p81 (c243), long-balls p76 (c229) |
| 6 | Javi Montero | Málaga | 78.7 | 2305 | long-balls p96 (c287), long-balls-won p93 (c278), accurate-passes-percentage p54 (c163) |
| 7 | Peru Rodríguez | Cultural Leonesa | 74.1 | 1870 | long-balls-won p100 (c300), long-balls p100 (c300), passes p87 (c130) |
| 8 | Loïc Williams | Granada | 73.3 | 2796 | long-balls p90 (c269), long-balls-won p82 (c247), accurate-passes-percentage p47 (c141) |
| 9 | Luken Beitia | Real Sociedad II | 71.8 | 2328 | long-balls-won p97 (c291), long-balls p93 (c278), accurate-passes-percentage p40 (c119) |
| 10 | Alberto Jiménez | Castellón | 70.9 | 3312 | accurate-passes-percentage p93 (c278), long-balls-won p68 (c203), long-balls p43 (c128) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Jair Amador | SD Eibar | 25.1 | 1473 | accurate-passes-percentage p62 (c185), passes p37 (c55), long-balls p7 (c22) |
| 2 | Oscar Naasei | Granada | 23.4 | 2790 | accurate-passes-percentage p32 (c97), long-balls-won p28 (c84), long-balls p22 (c66) |
| 3 | Martín Pascual | Mirandés | 21.6 | 1118 | long-balls-won p26 (c79), long-balls p16 (c49), accurate-passes-percentage p15 (c44) |
| 4 | Álvaro Carrillo | Huesca | 21.1 | 2308 | long-balls p40 (c119), long-balls-won p31 (c93), interceptions p26 (c13) |
| 5 | Manu Hernando | Racing Santander | 20.4 | 1957 | accurate-passes-percentage p46 (c137), passes p22 (c33), interceptions p65 (c32) |
| 6 | Bojan Kovacevic | Cádiz | 18.8 | 1825 | long-balls p25 (c75), accurate-passes-percentage p22 (c66), long-balls-won p9 (c26) |
| 7 | Jorge Pulido | Huesca | 17.2 | 3196 | accurate-passes-percentage p21 (c62), interceptions p88 (c44), long-balls-won p12 (c35) |
| 8 | Diego Sánchez | Sporting Gijón | 15.1 | 2916 | long-balls-won p24 (c71), long-balls p18 (c53), accurate-passes-percentage p7 (c22) |
| 9 | Sergio Arribas | Cádiz | 10.6 | 1356 | long-balls p24 (c71), interceptions p29 (c15), long-balls-won p4 (c13) |
| 10 | Carlos Hernández | Ceuta | 8.1 | 3433 | accurate-passes-percentage p18 (c53), interceptions p72 (c36), long-balls-won p0 (c0) |

### Premier League 2025/2026

n = 66 · media 50.0 · mediana 51.8 · desv 17.8 · rango [9.1, 83.7]

```
    0-10  | ## 1
   10-20  | ##### 3
   20-30  | ########## 6
   30-40  | ############# 8
   40-50  | #################### 12
   50-60  | ############################ 17
   60-70  | ############### 9
   70-80  | ############ 7
   80-90  | ##### 3
   90-100 |  0
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Virgil van Dijk | Liverpool | 83.7 | 3420 | long-balls-won p92 (c277), long-balls p91 (c272), accurate-passes-percentage p74 (c222) |
| 2 | Lisandro Martínez | Manchester United | 83.1 | 1230 | long-balls p86 (c258), long-balls-won p86 (c258), accurate-passes-percentage p82 (c245) |
| 3 | Jan Paul van Hecke | Brighton & Hove Albion | 80.0 | 3211 | long-balls-won p94 (c282), long-balls p94 (c282), accurate-passes-percentage p48 (c143) |
| 4 | Lewis Dunk | Brighton & Hove Albion | 77.8 | 2836 | accurate-passes-percentage p92 (c277), long-balls-won p77 (c231), long-balls p58 (c175) |
| 5 | Joachim Andersen | Fulham | 77.8 | 2877 | long-balls-won p98 (c295), long-balls p97 (c291), passes p92 (c138) |
| 6 | Fabian Schär | Newcastle United | 75.7 | 1090 | long-balls-won p100 (c300), long-balls p98 (c295), passes p83 (c125) |
| 7 | Pau Torres | Aston Villa | 74.2 | 1680 | long-balls-won p82 (c245), long-balls p77 (c231), accurate-passes-percentage p75 (c226) |
| 8 | Jorge Cuenca | Fulham | 73.4 | 939 | long-balls p85 (c254), long-balls-won p69 (c208), accurate-passes-percentage p65 (c194) |
| 9 | Tyrone Mings | Aston Villa | 72.9 | 1323 | accurate-passes-percentage p83 (c249), long-balls-won p74 (c222), long-balls p68 (c203) |
| 10 | Abdukodir Khusanov | Manchester City | 72.9 | 1429 | accurate-passes-percentage p89 (c268), long-balls-won p72 (c217), long-balls p46 (c138) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Maximilian Kilman | West Ham United | 29.9 | 1558 | accurate-passes-percentage p57 (c171), long-balls p34 (c102), long-balls-won p14 (c42) |
| 2 | Axel Tuanzebe | Burnley | 28.9 | 1203 | long-balls p43 (c129), accurate-passes-percentage p25 (c74), long-balls-won p20 (c60) |
| 3 | Maxime Estève | Burnley | 27.5 | 2938 | accurate-passes-percentage p43 (c129), long-balls p25 (c74), long-balls-won p15 (c46) |
| 4 | Hjalmar Ekdal | Burnley | 27.0 | 1540 | long-balls p40 (c120), accurate-passes-percentage p28 (c83), long-balls-won p25 (c74) |
| 5 | Joe Rodon | Leeds United | 22.4 | 2953 | accurate-passes-percentage p52 (c157), passes p28 (c42), interceptions p49 (c25) |
| 6 | Jean-Clair Todibo | West Ham United | 21.1 | 1820 | accurate-passes-percentage p51 (c152), long-balls p11 (c32), long-balls-won p8 (c23) |
| 7 | Lutsharel Geertruida | Sunderland | 17.9 | 1685 | accurate-passes-percentage p37 (c111), long-balls-won p12 (c37), interceptions p57 (c28) |
| 8 | Dan Burn | Newcastle United | 14.1 | 2199 | long-balls p26 (c78), passes p25 (c37), interceptions p34 (c17) |
| 9 | Kristoffer Ajer | Brentford | 13.7 | 1811 | long-balls p28 (c83), long-balls-won p11 (c32), interceptions p38 (c19) |
| 10 | Yerson Mosquera | Wolverhampton Wanderers | 9.1 | 2142 | long-balls p14 (c42), interceptions p80 (c40), accurate-passes-percentage p6 (c18) |

### Serie A 2025/2026

n = 72 · media 50.0 · mediana 47.0 · desv 17.9 · rango [12.7, 85.0]

```
    0-10  |  0
   10-20  | ##### 3
   20-30  | ############## 9
   30-40  | ############## 9
   40-50  | ############################ 18
   50-60  | ################ 10
   60-70  | ################# 11
   70-80  | ############## 9
   80-90  | ##### 3
   90-100 |  0
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Mario Gila | Lazio | 85.0 | 2484 | long-balls-won p100 (c300), long-balls p93 (c279), accurate-passes-percentage p72 (c215) |
| 2 | Oumar Solet | Udinese | 83.3 | 2961 | long-balls-won p99 (c296), long-balls p97 (c292), accurate-passes-percentage p55 (c165) |
| 3 | Jhon Lucumí | Bologna | 83.3 | 2287 | long-balls-won p97 (c292), long-balls p94 (c283), accurate-passes-percentage p61 (c182) |
| 4 | Juan Jesus | Napoli | 78.0 | 1676 | accurate-passes-percentage p83 (c249), long-balls-won p79 (c237), long-balls p62 (c186) |
| 5 | Alessandro Bastoni | Inter | 78.0 | 2251 | long-balls p99 (c296), long-balls-won p96 (c287), passes p97 (c146) |
| 6 | Torbjørn Heggem | Bologna | 76.4 | 2112 | long-balls-won p93 (c279), accurate-passes-percentage p87 (c262), long-balls p70 (c211) |
| 7 | Matteo Gabbia | AC Milan | 75.9 | 2530 | long-balls-won p90 (c270), accurate-passes-percentage p89 (c266), long-balls p72 (c215) |
| 8 | Manuel Akanji | Inter | 74.3 | 2820 | accurate-passes-percentage p92 (c275), long-balls-won p85 (c254), passes p90 (c135) |
| 9 | Oliver Provstgaard | Lazio | 74.1 | 1524 | accurate-passes-percentage p94 (c283), long-balls-won p72 (c215), long-balls p54 (c161) |
| 10 | Lloyd Kelly | Juventus | 73.9 | 2997 | long-balls-won p94 (c283), long-balls p87 (c262), accurate-passes-percentage p51 (c152) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Christian Kabasele | Udinese | 27.9 | 2257 | accurate-passes-percentage p44 (c131), long-balls-won p28 (c85), long-balls p14 (c42) |
| 2 | Jay Idzes | Sassuolo | 27.2 | 3064 | accurate-passes-percentage p65 (c194), interceptions p62 (c31), passes p18 (c27) |
| 3 | Guillermo Maripán | Torino | 26.7 | 2146 | long-balls p30 (c89), long-balls-won p30 (c89), accurate-passes-percentage p21 (c63) |
| 4 | Tiago Gabriel | Lecce | 26.4 | 3220 | accurate-passes-percentage p37 (c110), long-balls-won p27 (c80), long-balls p17 (c51) |
| 5 | Juan Rodríguez | Cagliari | 24.5 | 1315 | accurate-passes-percentage p48 (c144), long-balls p15 (c46), passes p27 (c40) |
| 6 | Honest Ahanor | Atalanta | 24.1 | 1375 | accurate-passes-percentage p58 (c173), passes p32 (c49), interceptions p86 (c43) |
| 7 | Armel Bella-Kotchap | Hellas Verona | 23.2 | 1346 | long-balls p31 (c93), accurate-passes-percentage p17 (c51), interceptions p100 (c50) |
| 8 | Arturo Calabresi | Pisa | 18.8 | 1520 | long-balls p28 (c85), long-balls-won p23 (c68), accurate-passes-percentage p10 (c30) |
| 9 | Alessandro Marcandalli | Genoa | 16.9 | 2600 | long-balls p21 (c63), long-balls-won p17 (c51), accurate-passes-percentage p11 (c34) |
| 10 | Victor Nelsson | Hellas Verona | 12.7 | 3316 | interceptions p97 (c49), accurate-passes-percentage p14 (c42), long-balls p10 (c30) |

### Bundesliga 2025/2026

n = 63 · media 50.0 · mediana 48.4 · desv 17.0 · rango [11.1, 83.2]

```
    0-10  |  0
   10-20  | ## 1
   20-30  | ########## 6
   30-40  | ########################## 16
   40-50  | ############### 9
   50-60  | ############ 7
   60-70  | ############################ 17
   70-80  | ######## 5
   80-90  | ### 2
   90-100 |  0
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Nico Schlotterbeck | Borussia Dortmund | 83.2 | 2520 | long-balls p100 (c300), long-balls-won p100 (c300), accurate-passes-percentage p60 (c179) |
| 2 | Edmond Tapsoba | Bayer 04 Leverkusen | 81.9 | 2576 | long-balls-won p87 (c261), accurate-passes-percentage p84 (c252), long-balls p81 (c242) |
| 3 | Marco Friedl | Werder Bremen | 78.1 | 2548 | long-balls-won p97 (c290), long-balls p82 (c247), accurate-passes-percentage p63 (c189) |
| 4 | Philipp Lienhart | SC Freiburg | 75.2 | 1301 | long-balls p77 (c232), long-balls-won p77 (c232), accurate-passes-percentage p77 (c232) |
| 5 | Amos Pieper | Werder Bremen | 74.5 | 1506 | long-balls p95 (c285), long-balls-won p95 (c285), accurate-passes-percentage p37 (c111) |
| 6 | Arthur Theate | Eintracht Frankfurt | 74.0 | 2144 | long-balls-won p85 (c256), accurate-passes-percentage p73 (c218), long-balls p63 (c189) |
| 7 | Robin Koch | Eintracht Frankfurt | 72.1 | 2835 | accurate-passes-percentage p89 (c266), long-balls-won p68 (c203), long-balls p56 (c169) |
| 8 | Dayot Upamecano | FC Bayern München | 69.6 | 1799 | accurate-passes-percentage p94 (c281), long-balls-won p69 (c208), passes p95 (c143) |
| 9 | Jeff Chabot | VfB Stuttgart | 69.5 | 2296 | long-balls-won p81 (c242), accurate-passes-percentage p61 (c184), long-balls p60 (c179) |
| 10 | Albian Hajdari | TSG Hoffenheim | 69.0 | 2440 | long-balls p97 (c290), long-balls-won p92 (c276), passes p61 (c92) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Arthur Chaves | TSG Hoffenheim | 30.9 | 1067 | long-balls p52 (c155), long-balls-won p37 (c111), accurate-passes-percentage p16 (c48) |
| 2 | Bruno Ogbus | SC Freiburg | 30.6 | 1177 | accurate-passes-percentage p87 (c261), passes p32 (c48), long-balls p5 (c15) |
| 3 | Tomoya Ando | St. Pauli | 30.6 | 1261 | accurate-passes-percentage p40 (c121), long-balls p29 (c87), passes p39 (c58) |
| 4 | Cédric Zesiger | FC Augsburg | 29.3 | 1812 | long-balls p53 (c160), long-balls-won p23 (c68), passes p31 (c46) |
| 5 | Adam Dzwigala | St. Pauli | 28.8 | 1292 | long-balls p39 (c116), long-balls-won p29 (c87), interceptions p92 (c46) |
| 6 | Jeanuël Belocian | Bayer 04 Leverkusen | 26.6 | 1544 | accurate-passes-percentage p65 (c194), long-balls-won p13 (c39), passes p19 (c29) |
| 7 | Patrick Mainka | FC Heidenheim | 22.9 | 3060 | accurate-passes-percentage p50 (c150), long-balls p11 (c34), long-balls-won p10 (c29) |
| 8 | Joël Schmied | FC Köln | 20.8 | 1081 | accurate-passes-percentage p56 (c169), long-balls-won p8 (c24), long-balls p8 (c24) |
| 9 | Kacper Potulski | FSV Mainz 05 | 20.0 | 1060 | long-balls p23 (c68), accurate-passes-percentage p18 (c53), long-balls-won p16 (c48) |
| 10 | Nicolás Capaldo | Hamburger SV | 11.1 | 2011 | long-balls p16 (c48), interceptions p89 (c44), accurate-passes-percentage p8 (c24) |


---

## Central Dominante

### La Liga 2024/2025

n = 63 · media 50.0 · mediana 49.6 · desv 18.7 · rango [14.4, 85.2]

```
    0-10  |  0
   10-20  | ###### 3
   20-30  | ############### 7
   30-40  | ############################ 13
   40-50  | ################### 9
   50-60  | ###################### 10
   60-70  | ################### 9
   70-80  | ################# 8
   80-90  | ######### 4
   90-100 |  0
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Jorge Sáenz | Leganés | 85.2 | 1691 | clearances p98 (c295), duels-won p95 (c285), aeriels-won p61 (c184) |
| 2 | Aridane Hernández | Rayo Vallecano | 80.8 | 1024 | aeriels-won p100 (c300), clearances p100 (c300), duels-won p98 (c295) |
| 3 | Omar Alderete | Getafe | 80.7 | 2978 | clearances p95 (c285), duels-won p94 (c281), aeriels-won p90 (c271) |
| 4 | Kike Salas | Sevilla | 80.1 | 2236 | duels-won p97 (c290), aeriels-won p97 (c290), clearances p69 (c208) |
| 5 | Marash Kumbulla | Espanyol | 76.3 | 2976 | clearances p89 (c266), duels-won p74 (c223), aeriels-won p66 (c198) |
| 6 | Juan Foyth | Villarreal | 75.5 | 1526 | clearances p90 (c271), aeriels-won p76 (c227), duels-won p65 (c194) |
| 7 | Antonio Raíllo | Mallorca | 75.5 | 3209 | aeriels-won p98 (c295), clearances p84 (c252), duels-won p81 (c242) |
| 8 | Marc Bartra | Real Betis | 75.4 | 2101 | clearances p82 (c247), duels-won p71 (c213), aeriels-won p65 (c194) |
| 9 | Carlos Domínguez | Celta de Vigo | 75.2 | 1181 | duels-won p85 (c256), clearances p71 (c213), aeriels-won p71 (c213) |
| 10 | Diego Llorente | Real Betis | 74.7 | 2521 | duels-won p90 (c271), aeriels-won p87 (c261), clearances p65 (c194) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Pau Cubarsí | FC Barcelona | 29.7 | 2620 | aeriels-won p63 (c189), duels-won p32 (c97), tackles p26 (c39) |
| 2 | Eray Cömert | Real Valladolid | 28.1 | 1785 | blocked-shots p63 (c94), tackles p55 (c82), duels-won p21 (c63) |
| 3 | Willy Kambwala | Villarreal | 26.8 | 1114 | clearances p35 (c106), tackles p60 (c90), blocked-shots p42 (c63) |
| 4 | Logan Costa | Villarreal | 26.6 | 2585 | aeriels-won p37 (c111), clearances p26 (c77), tackles p52 (c77) |
| 5 | David Torres | Real Valladolid | 26.3 | 1386 | blocked-shots p95 (c143), clearances p39 (c116), aeriels-won p15 (c44) |
| 6 | Cristhian Mosquera | Valencia | 24.1 | 3321 | tackles p61 (c92), blocked-shots p47 (c70), duels-won p19 (c58) |
| 7 | Dakonam Djené | Getafe | 20.1 | 2555 | aeriels-won p31 (c92), duels-won p26 (c77), clearances p16 (c48) |
| 8 | David López | Girona | 19.9 | 2431 | clearances p31 (c92), tackles p34 (c51), blocked-shots p26 (c39) |
| 9 | Daley Blind | Girona | 17.3 | 2778 | tackles p76 (c114), duels-won p15 (c44), interceptions p55 (c27) |
| 10 | Antonio Rüdiger | Real Madrid | 14.4 | 2290 | clearances p23 (c68), aeriels-won p16 (c48), blocked-shots p27 (c41) |

### La Liga 2025/2026

n = 69 · media 50.0 · mediana 51.9 · desv 17.6 · rango [9.1, 89.9]

```
    0-10  | ## 1
   10-20  | ####### 4
   20-30  | ## 1
   30-40  | ############################ 16
   40-50  | ################## 10
   50-60  | ########################## 15
   60-70  | ####################### 13
   70-80  | ########## 6
   80-90  | ##### 3
   90-100 |  0
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Kike Salas | Sevilla | 89.9 | 2202 | aeriels-won p100 (c300), duels-won p100 (c300), clearances p88 (c265) |
| 2 | David Carmo | Real Oviedo | 80.9 | 1787 | clearances p97 (c291), aeriels-won p91 (c274), duels-won p78 (c234) |
| 3 | Diego Llorente | Real Betis | 80.4 | 1229 | clearances p93 (c278), duels-won p82 (c247), aeriels-won p79 (c238) |
| 4 | Marc Pubill | Atlético de Madrid | 78.3 | 1382 | duels-won p99 (c296), aeriels-won p99 (c296), clearances p51 (c154) |
| 5 | Jon Martín | Real Sociedad | 77.5 | 2250 | aeriels-won p96 (c287), duels-won p90 (c269), clearances p74 (c221) |
| 6 | Marc Bartra | Real Betis | 75.7 | 1976 | clearances p94 (c282), duels-won p69 (c207), aeriels-won p53 (c159) |
| 7 | Dani Calvo | Real Oviedo | 71.6 | 1608 | clearances p100 (c300), aeriels-won p76 (c229), blocked-shots p99 (c148) |
| 8 | José María Giménez | Atlético de Madrid | 70.9 | 1176 | duels-won p94 (c282), aeriels-won p88 (c265), tackles p75 (c112) |
| 9 | Vitor Reis | Girona | 70.5 | 3138 | aeriels-won p78 (c234), duels-won p72 (c216), clearances p71 (c212) |
| 10 | Eric Bailly | Real Oviedo | 68.9 | 1236 | aeriels-won p90 (c269), duels-won p71 (c212), clearances p68 (c203) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Fernando Calero | Espanyol | 32.5 | 2150 | blocked-shots p94 (c141), clearances p40 (c119), aeriels-won p24 (c71) |
| 2 | Clément Lenglet | Atlético de Madrid | 32.3 | 1394 | aeriels-won p50 (c150), clearances p25 (c75), duels-won p24 (c71) |
| 3 | Dakonam Djené | Getafe | 30.6 | 2586 | clearances p35 (c106), duels-won p34 (c101), aeriels-won p29 (c88) |
| 4 | Dani Vivian | Athletic Club | 30.5 | 2563 | tackles p78 (c117), clearances p34 (c101), duels-won p22 (c66) |
| 5 | Enzo Boyomo | Osasuna | 24.1 | 2545 | tackles p85 (c128), clearances p18 (c53), aeriels-won p15 (c44) |
| 6 | Dávid Hancko | Atlético de Madrid | 19.4 | 2433 | aeriels-won p25 (c75), tackles p47 (c71), duels-won p12 (c35) |
| 7 | Aitor Paredes | Athletic Club | 18.9 | 1629 | aeriels-won p32 (c97), interceptions p93 (c46), clearances p15 (c44) |
| 8 | Javi Rodríguez | Celta de Vigo | 16.3 | 2560 | blocked-shots p40 (c60), duels-won p18 (c53), tackles p32 (c49) |
| 9 | Antonio Rüdiger | Real Madrid | 11.7 | 1491 | aeriels-won p40 (c119), clearances p4 (c13), blocked-shots p3 (c4) |
| 10 | Raúl Asencio | Real Madrid | 9.1 | 1707 | blocked-shots p43 (c64), duels-won p6 (c18), aeriels-won p4 (c13) |

### La Liga 2 2025/2026

n = 69 · media 50.0 · mediana 52.4 · desv 18.7 · rango [13.2, 87.8]

```
    0-10  |  0
   10-20  | ######### 4
   20-30  | ################# 8
   30-40  | ########################## 12
   40-50  | ###################### 10
   50-60  | ############################ 13
   60-70  | ###################### 10
   70-80  | ###################### 10
   80-90  | #### 2
   90-100 |  0
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Carlos Hernández | Ceuta | 87.8 | 3433 | aeriels-won p99 (c296), duels-won p93 (c278), clearances p88 (c265) |
| 2 | Pablo Vázquez | Sporting Gijón | 83.2 | 3135 | aeriels-won p97 (c291), duels-won p90 (c269), clearances p90 (c269) |
| 3 | Jorge Pulido | Huesca | 79.1 | 3196 | clearances p94 (c282), aeriels-won p85 (c256), duels-won p74 (c221) |
| 4 | Javi Moreno | Albacete | 78.6 | 1453 | duels-won p97 (c291), aeriels-won p90 (c269), clearances p68 (c203) |
| 5 | Martín Pascual | Mirandés | 78.5 | 1118 | aeriels-won p100 (c300), clearances p99 (c296), duels-won p94 (c282) |
| 6 | Rubén Alves | Córdoba | 78.3 | 1640 | clearances p100 (c300), aeriels-won p91 (c274), duels-won p87 (c260) |
| 7 | Kazunari Kita | Real Sociedad II | 77.8 | 2385 | aeriels-won p93 (c278), clearances p82 (c247), duels-won p69 (c207) |
| 8 | Sergio Barcia | Las Palmas | 76.0 | 3020 | aeriels-won p96 (c287), duels-won p84 (c251), clearances p76 (c229) |
| 9 | Xavi Sintes | Córdoba | 75.7 | 2078 | duels-won p88 (c265), aeriels-won p81 (c243), clearances p75 (c225) |
| 10 | Lucas Perrin | Sporting Gijón | 74.5 | 1952 | duels-won p79 (c238), clearances p78 (c234), aeriels-won p63 (c190) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Marvelous Antolín Garzón | Leganés | 28.9 | 3069 | duels-won p51 (c154), tackles p74 (c110), interceptions p74 (c37) |
| 2 | Aitor Córdoba | Burgos | 27.4 | 1565 | clearances p56 (c168), blocked-shots p56 (c84), aeriels-won p26 (c79) |
| 3 | Pablo Tomeo | Real Valladolid | 27.3 | 2961 | tackles p68 (c101), clearances p25 (c75), duels-won p24 (c71) |
| 4 | Anaitz Arbilla | SD Eibar | 26.9 | 2891 | tackles p71 (c106), duels-won p28 (c84), interceptions p94 (c47) |
| 5 | Jesús Vallejo | Albacete | 26.2 | 2460 | aeriels-won p47 (c141), clearances p28 (c84), blocked-shots p28 (c42) |
| 6 | Diego Sánchez | Sporting Gijón | 22.8 | 2916 | aeriels-won p31 (c93), duels-won p29 (c88), tackles p38 (c57) |
| 7 | Ramón Martínez | Real Valladolid | 18.1 | 1257 | tackles p65 (c97), blocked-shots p32 (c49), duels-won p13 (c40) |
| 8 | Arnau Comas | Deportivo A Coruña | 17.5 | 1578 | blocked-shots p47 (c71), clearances p16 (c49), tackles p26 (c40) |
| 9 | Nélson Monte | Almería | 15.6 | 2465 | blocked-shots p49 (c73), interceptions p81 (c40), clearances p13 (c40) |
| 10 | Oscar Naasei | Granada | 13.2 | 2790 | tackles p57 (c86), duels-won p22 (c66), interceptions p16 (c8) |

### Premier League 2025/2026

n = 66 · media 50.0 · mediana 52.8 · desv 20.0 · rango [4.4, 87.8]

```
    0-10  | ## 1
   10-20  | ########## 5
   20-30  | ########## 5
   30-40  | ############################ 14
   40-50  | ######## 4
   50-60  | ############################ 14
   60-70  | ######################## 12
   70-80  | ############## 7
   80-90  | ######## 4
   90-100 |  0
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Kevin Danso | Tottenham Hotspur | 87.8 | 1500 | clearances p100 (c300), duels-won p98 (c295), aeriels-won p98 (c295) |
| 2 | Dan Ballard | Sunderland | 86.0 | 2148 | clearances p98 (c295), duels-won p95 (c286), aeriels-won p94 (c282) |
| 3 | James Hill | AFC Bournemouth | 84.2 | 2112 | aeriels-won p100 (c300), duels-won p97 (c291), clearances p91 (c272) |
| 4 | Sven Botman | Newcastle United | 80.5 | 1838 | aeriels-won p92 (c277), duels-won p92 (c277), clearances p80 (c240) |
| 5 | James Tarkowski | Everton | 79.5 | 3330 | duels-won p89 (c268), aeriels-won p89 (c268), clearances p74 (c222) |
| 6 | Maxence Lacroix | Crystal Palace | 76.2 | 3087 | clearances p95 (c286), duels-won p86 (c258), aeriels-won p78 (c235) |
| 7 | Michael Keane | Everton | 76.2 | 2590 | aeriels-won p88 (c263), clearances p86 (c258), duels-won p74 (c222) |
| 8 | Wesley Fofana | Chelsea | 72.5 | 1727 | duels-won p85 (c254), aeriels-won p82 (c245), clearances p75 (c226) |
| 9 | Jaydee Canvot | Crystal Palace | 72.1 | 1333 | clearances p83 (c249), duels-won p82 (c245), aeriels-won p49 (c148) |
| 10 | Marcos Senesi | AFC Bournemouth | 71.5 | 3290 | clearances p82 (c245), duels-won p63 (c189), aeriels-won p52 (c157) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Jean-Clair Todibo | West Ham United | 27.0 | 1820 | tackles p85 (c127), clearances p32 (c97), blocked-shots p26 (c39) |
| 2 | Lisandro Martínez | Manchester United | 26.6 | 1230 | blocked-shots p63 (c95), tackles p60 (c90), clearances p25 (c74) |
| 3 | Josko Gvardiol | Manchester City | 25.9 | 1374 | aeriels-won p31 (c92), blocked-shots p45 (c67), duels-won p20 (c60) |
| 4 | Abdukodir Khusanov | Manchester City | 22.0 | 1429 | tackles p77 (c115), interceptions p98 (c49), duels-won p15 (c46) |
| 5 | Pau Torres | Aston Villa | 18.4 | 1680 | blocked-shots p71 (c106), tackles p35 (c53), aeriels-won p12 (c37) |
| 6 | Micky van de Ven | Tottenham Hotspur | 18.3 | 3044 | duels-won p18 (c55), tackles p32 (c48), aeriels-won p15 (c46) |
| 7 | Lutsharel Geertruida | Sunderland | 15.8 | 1685 | tackles p86 (c129), interceptions p57 (c28), duels-won p9 (c28) |
| 8 | Axel Disasi | West Ham United | 15.0 | 1255 | blocked-shots p62 (c92), aeriels-won p11 (c32), tackles p15 (c23) |
| 9 | Ezri Konsa | Aston Villa | 13.1 | 3036 | blocked-shots p65 (c97), clearances p9 (c28), duels-won p5 (c14) |
| 10 | Victor Lindelöf | Aston Villa | 4.4 | 944 | aeriels-won p8 (c23), interceptions p22 (c11), tackles p6 (c9) |

### Serie A 2025/2026

n = 72 · media 50.0 · mediana 51.0 · desv 19.0 · rango [11.0, 86.7]

```
    0-10  |  0
   10-20  | ###### 3
   20-30  | ###################### 12
   30-40  | ############# 7
   40-50  | ###################### 12
   50-60  | ############################ 15
   60-70  | ######################## 13
   70-80  | ######### 5
   80-90  | ######### 5
   90-100 |  0
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Victor Nelsson | Hellas Verona | 86.7 | 3316 | aeriels-won p96 (c287), duels-won p94 (c283), clearances p93 (c279) |
| 2 | Nicolás Valentini | Hellas Verona | 86.1 | 1406 | duels-won p96 (c287), aeriels-won p92 (c275), clearances p85 (c254) |
| 3 | Tiago Gabriel | Lecce | 82.7 | 3220 | duels-won p99 (c296), aeriels-won p94 (c283), clearances p89 (c266) |
| 4 | Andrias Edmundsson | Hellas Verona | 81.8 | 1320 | clearances p100 (c300), aeriels-won p82 (c245), duels-won p65 (c194) |
| 5 | Leo Østigård | Genoa | 81.2 | 2624 | aeriels-won p100 (c300), clearances p96 (c287), duels-won p82 (c245) |
| 6 | Berat Djimsiti | Atalanta | 77.9 | 2526 | aeriels-won p90 (c270), duels-won p79 (c237), clearances p66 (c199) |
| 7 | Guillermo Maripán | Torino | 77.8 | 2146 | clearances p83 (c249), duels-won p70 (c211), aeriels-won p70 (c211) |
| 8 | Martin Vitík | Bologna | 76.2 | 1323 | duels-won p90 (c270), aeriels-won p86 (c258), clearances p82 (c245) |
| 9 | Ardian Ismajli | Torino | 75.0 | 1906 | clearances p99 (c296), aeriels-won p69 (c207), duels-won p66 (c199) |
| 10 | Armel Bella-Kotchap | Hellas Verona | 75.0 | 1346 | aeriels-won p79 (c237), clearances p77 (c232), duels-won p72 (c215) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Yann Bisseck | Inter | 25.9 | 1922 | duels-won p38 (c114), aeriels-won p31 (c93), tackles p34 (c51) |
| 2 | Manuel Akanji | Inter | 23.5 | 2820 | tackles p49 (c74), duels-won p24 (c72), aeriels-won p21 (c63) |
| 3 | Alessandro Marcandalli | Genoa | 22.6 | 2600 | aeriels-won p35 (c106), clearances p20 (c59), duels-won p18 (c55) |
| 4 | Sebastiano Luperto | Cremonese | 22.5 | 3017 | clearances p54 (c161), blocked-shots p35 (c53), tackles p21 (c32) |
| 5 | Enzo Ebosse | Hellas Verona | 20.7 | 1334 | blocked-shots p83 (c125), clearances p31 (c93), aeriels-won p7 (c21) |
| 6 | Filippo Terracciano | Cremonese | 20.6 | 3012 | blocked-shots p52 (c78), clearances p15 (c46), interceptions p92 (c46) |
| 7 | Sead Kolasinac | Atalanta | 20.0 | 1219 | tackles p83 (c125), duels-won p31 (c93), aeriels-won p4 (c13) |
| 8 | Odilon Kossounou | Atalanta | 19.1 | 984 | tackles p54 (c80), blocked-shots p41 (c61), duels-won p13 (c38) |
| 9 | Sam Beukema | Napoli | 14.8 | 1679 | aeriels-won p25 (c76), blocked-shots p32 (c49), tackles p20 (c30) |
| 10 | Pierre Kalulu | Juventus | 11.0 | 3282 | tackles p65 (c97), duels-won p10 (c30), aeriels-won p3 (c8) |

### Bundesliga 2025/2026

n = 63 · media 50.0 · mediana 48.0 · desv 19.6 · rango [14.6, 84.3]

```
    0-10  |  0
   10-20  | ############ 5
   20-30  | ############## 6
   30-40  | ########################## 11
   40-50  | ############################ 12
   50-60  | ################ 7
   60-70  | ########################## 11
   70-80  | ############## 6
   80-90  | ############ 5
   90-100 |  0
```

**Top-10**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Luka Vuskovic | Hamburger SV | 84.3 | 2442 | clearances p98 (c295), aeriels-won p98 (c295), duels-won p97 (c290) |
| 2 | Willi Orbán | RB Leipzig | 83.2 | 2950 | aeriels-won p89 (c266), clearances p89 (c266), duels-won p89 (c266) |
| 3 | Leopold Querfeld | FC Union Berlin | 82.7 | 2704 | duels-won p94 (c281), aeriels-won p90 (c271), clearances p87 (c261) |
| 4 | Stefan Bell | FSV Mainz 05 | 81.2 | 1050 | aeriels-won p97 (c290), clearances p97 (c290), duels-won p92 (c276) |
| 5 | Patrick Mainka | FC Heidenheim | 80.7 | 3060 | aeriels-won p92 (c276), clearances p90 (c271), duels-won p84 (c252) |
| 6 | Jeff Chabot | VfB Stuttgart | 79.5 | 2296 | duels-won p100 (c300), aeriels-won p95 (c285), clearances p92 (c276) |
| 7 | Amos Pieper | Werder Bremen | 79.1 | 1506 | clearances p84 (c252), aeriels-won p77 (c232), duels-won p76 (c227) |
| 8 | Ozan Kabak | TSG Hoffenheim | 78.9 | 1752 | aeriels-won p100 (c300), duels-won p98 (c295), clearances p85 (c256) |
| 9 | Robin Koch | Eintracht Frankfurt | 71.8 | 2835 | aeriels-won p85 (c256), clearances p82 (c247), duels-won p65 (c194) |
| 10 | Stefan Posch | FSV Mainz 05 | 71.6 | 1396 | duels-won p90 (c271), aeriels-won p68 (c203), clearances p55 (c165) |

**Bottom-10 (de los que sí puntúan)**

| # | jugador | equipo | score | min | métricas top (percentil, contribución) |
|---|---|---|---|---|---|
| 1 | Castello Lukeba | RB Leipzig | 29.1 | 2176 | blocked-shots p71 (c106), clearances p34 (c102), duels-won p19 (c58) |
| 2 | Jeanuël Belocian | Bayer 04 Leverkusen | 27.5 | 1544 | tackles p82 (c123), blocked-shots p58 (c87), duels-won p27 (c82) |
| 3 | Dayot Upamecano | FC Bayern München | 26.8 | 1799 | tackles p90 (c135), duels-won p39 (c116), aeriels-won p23 (c68) |
| 4 | Daniel Elfadli | Hamburger SV | 26.8 | 1254 | duels-won p31 (c92), tackles p58 (c87), clearances p16 (c48) |
| 5 | Warmed Omari | Hamburger SV | 23.7 | 1607 | blocked-shots p56 (c85), clearances p24 (c73), tackles p37 (c56) |
| 6 | Karim Coulibaly | Werder Bremen | 19.0 | 2122 | clearances p23 (c68), blocked-shots p40 (c60), aeriels-won p15 (c44) |
| 7 | Eric Smith | St. Pauli | 17.7 | 2313 | duels-won p21 (c63), tackles p42 (c63), blocked-shots p34 (c51) |
| 8 | Jarell Quansah | Bayer 04 Leverkusen | 16.8 | 2300 | duels-won p23 (c68), aeriels-won p16 (c48), blocked-shots p24 (c36) |
| 9 | Hiroki Ito | FC Bayern München | 14.8 | 921 | aeriels-won p42 (c126), interceptions p61 (c31), clearances p8 (c24) |
| 10 | Joël Schmied | FC Köln | 14.6 | 1081 | blocked-shots p61 (c92), aeriels-won p13 (c39), clearances p10 (c29) |

