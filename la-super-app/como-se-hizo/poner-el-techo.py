#!/usr/bin/env python3
"""Pone en CADA sección su techo propio, medido, con lo que falta para llegar —
y dice, en la misma línea, si un refutador lo revisó y qué sobrevivió.

🔴 «Verde» es del candado; «hecho» es del refutador. Un número que todavía no
   pasó por un refutador se publica DICIENDO que no pasó, nunca callándolo.

🔴 Lo que este script NO hace: declarar que los números nuevos «corrigen» los
   viejos. El cuadro del 20-sep mide 8 MOMENTOS con su propio método; esto mide
   15 SECCIONES con otro. Cambiar sujeto e instrumento a la vez y publicar la
   resta es lo que tumbó el 7,88 de la Tienda.
"""
import json, re, html, os

# 🔑 Las rutas de la Mac NO se publican, pero el script tiene que poder correrse
#    de nuevo: un «cómo se hizo» que no se puede repetir es una foto, no un
#    método. Salen del ambiente:
#        SCRATCHPAD=<carpeta con mediciones.json> DOC=<index.html> \
#        RAICES_A_TAPAR=<ruta>=<qué decir>:<ruta>=<qué decir> python3 este.py
#
# 🔴 POR QUÉ ASÍ, y es un defecto medido el 23-sep-2026 01:2x -03: la copia que
#    se publicaba de este archivo se limpiaba con esta misma tabla, así que
#    **los PATRONES se limpiaban a sí mismos** y quedaban en
#    `(r'', '')` — que matchea la cadena vacía en todas partes— y en pares
#    idénticos que no reemplazan nada. El saneador publicado estaba MUERTO y su
#    `assert` no lo podía cazar, porque el assert corre sobre el documento, no
#    sobre el saneador. Sacando los literales del código, no hay nada que limpiar.
SCR = os.environ.get('SCRATCHPAD', '(scratchpad)')
DOC = os.environ.get('DOC', 'este documento')
med    = json.load(open(f'{SCR}/mediciones.json', encoding='utf-8'))
try:    refut = json.load(open(f'{SCR}/refutaciones.json', encoding='utf-8'))
except: refut = {}

med.setdefault('s11', json.load(open(f'{SCR}/s11.json', encoding='utf-8')))

def coma(x):
    try: return f'{float(x):.2f}'.replace('.', ',')
    except Exception: return '—'

def nombre_de_app(bruto):
    """El nombre de la app sola.

    🃏 Los frentes escriben en `appLider` la app Y lo que se ve en su lamina
       —«Swiggy · el buscador dice "Search for Onion"»—, que es dato valioso y
       va a la tabla. Pero en el renglon «medido contra ...» eso produce una
       frase de 90 caracteres donde tiene que ir un nombre. Se parte por el
       primer separador y se descartan los que no nombran a nadie.
    """
    a = (bruto or '').strip()
    if not a: return None
    for sep in (' · ', ': ', ' — ', ' (', ','):
        if sep in a: a = a.split(sep)[0].strip()
    a = re.sub(r'\s+[0-9a-f]{8}$', '', a).strip(' ·—-')
    if not a: return None
    bajo = a.lower()
    # lo que no es una app: una norma, un «no pude medir», una vara propia
    if (bajo.startswith(('no pude medir', 'no comparable', 'compuesto', 'norma',
                         'techo de la lista', 'vara', '(vara'))
        or len(a) > 30 or len(a) < 2): return None
    return a

def lideres_de(r):
    apps = []
    for v in r.get('variables', []):
        a = nombre_de_app(v.get('appLider'))
        if a and a not in apps: apps.append(a)
    for a in r.get('lideres', []):
        a = nombre_de_app(a)
        if a and a not in apps: apps.append(a)
    return apps[:6]

def _sinNombre(r):
    """Que decir cuando el frente cito la lamina y no el nombre de la app.

    🔑 Lo auditable es la LAMINA, no el nombre: un nombre de app sin lamina no
       se puede comprobar, y una lamina sin nombre si. Entonces se dice cuantas
       laminas hay y se las lista abajo, en vez de escribir «las lideres» —que
       no nombra a nadie— o inventar un nombre.
    """
    n = sum(1 for v in r.get('variables', [])
            if v.get('laminaMobbin') and 'no pude' not in str(v['laminaMobbin']).lower())
    if n == 0: return 'una vara propia, sin lámina (ver abajo)'
    return f'{n} lámina{"s" if n != 1 else ""} de Mobbin, citadas una por una abajo'

# ═══ QUIEN NO SE PUDO MEDIR: NOSOTROS O LA LIDER ═══════════════════════════
#
# 🔴 EL DEFECTO QUE ESTO ARREGLA · medido el 23-sep-2026 01:1x -03, y lo trajo
#    el refutador de la seccion 11 (la unica de las 15 que no tenia uno).
#
#    El campo `noPudeMedir` de cada variable describe **el lado LIDER**, no el
#    nuestro. Sus propios denominadores lo dicen con todas las letras:
#      s8 accesibilidad: «Total 78/79 = 9,87. EL 2 ES DEL LADO LIDER, NO DEL
#                         NUESTRO»
#      s8 estados:       «= 3/4. EL 2 ES DEL LADO LIDER: de una lamina suelta
#                         de Mobbin no se puede contar cuantos estados dibuja»
#
#    Y el generador lo leia al reves, en las DOS columnas a la vez:
#      · NUESTRA columna imprimia «no pude medir» TAPANDO un numero medido
#        (9,87, con denominador 78/79). Cuatro celdas.
#      · La columna de la LIDER imprimia `coma(v.get('lider', 0))` sin mirar
#        nada, asi que un `lider = 2` —que es el CODIGO DE SALIDA «no pude
#        medir»— salia impreso «2,0» al lado de puntajes de verdad, como si la
#        app lider sacara 2 de 10. Cuatro celdas. Es la forma nº 8 de esta casa
#        (el `exit 2` degradado a veredicto) adentro del documento publico.
#
# 🧪 LOS DOS CONTROLES, corridos sobre las 120 variables de las 15 secciones:
#    · positivo: una variable medida de los dos lados da False en los dos.
#    · negativo: un denominador que MENCIONA «no pude medir» en el medio de la
#      frase NO cuenta — por eso se mira que ARRANQUE diciendolo, no que lo
#      contenga. Sin ese negativo, s8 caeria del lado equivocado y se borrarian
#      dos numeros que SI estan medidos.
#    Resultado: NUESTRO lado sin medir = 1 de 120 (s9 velocidad, cuyo
#    denominador arranca «NO PUDE MEDIR.»). Lado lider sin medir = 4 de 120.

def nuestroSinMedir(v):
    """¿NUESTRO numero no se pudo medir? Se decide por el denominador, que es
       donde vive la razon, y exigiendo que ARRANQUE diciendolo."""
    return str(v.get('denominador', '')).strip().lower().startswith('no pude medir')

def liderSinMedir(v):
    """¿El numero de la app LIDER no se pudo medir? Un `lider` ausente, o un 2
       acompanado de un `appLider` que dice que no se pudo."""
    l = v.get('lider')
    a = str(v.get('appLider', '')).lower()
    if l is None:
        return True
    return l == 2 and ('no pude' in a or not a or a == 'none')

# 🔴 ESTO ERA UN LITERAL, «14 secciones» y «ninguna salió confirmada», escrito a
#    mano · lo cazó el refutador de la sección 11 el 23-sep-2026: «el día que un
#    refutador confirme una, la página va a seguir diciendo 14 y ninguna».
#    Un número que no se mueve cuando cambia lo que dice medir no mide eso
#    (forma nº 18 de esta casa). Ahora se CUENTA.
def _cuantasRefutadas():
    return str(len(refut))

def _cuantasConfirmadas():
    c = sum(1 for v in refut.values() if str(v.get('veredicto', '')).upper() == 'CONFIRMADO')
    if c == 0:
        return 'ninguna salió confirmada del todo'
    return f'{c} salió confirmada' if c == 1 else f'{c} salieron confirmadas'

def bloque(sid, r):
    e = html.escape
    ref   = refut.get(sid)
    # 🔴 ACA DECIA `hoy = r.get('hoy', ...)` · 23-sep-2026 01:1x -03. El puntaje
    #    se LEIA de un campo declarado y no se derivaba nunca de la tabla que el
    #    lector tiene delante. En s11 eso publico 7,10 mientras su propia tabla
    #    daba 7,19. Ahora sale de la tabla, siempre, y se dice sobre cuantas.
    _vs = r.get('variables', []) or []
    _medidas = [v['hoy'] for v in _vs if not nuestroSinMedir(v)]
    hoy   = round(sum(_medidas) / len(_medidas), 2) if _medidas else r.get('hoy')
    _sobre = f'{len(_medidas)} de {len(_vs)}' if _vs else ''
    _sinMedirNuestro = [v['nombre'] for v in _vs if nuestroSinMedir(v)]
    techo = r.get('techo', r.get('techoRederivado'))
    nota_ref = ''
    if ref:
        sh, st = ref.get('puntajeQueSobrevive'), ref.get('techoQueSobrevive')
        cayeron = len(ref.get('afirmacionesTumbadas') or [])
        atajos  = len(ref.get('atajosHallados') or [])
        cambio = []
        if sh is not None and abs(float(sh) - float(hoy)) >= 0.005:
            cambio.append(f'el puntaje pasó de {coma(hoy)} a {coma(sh)}'); hoy = sh
        if st is not None and abs(float(st) - float(techo)) >= 0.005:
            cambio.append(f'el techo pasó de {coma(techo)} a {coma(st)}'); techo = st
        v = ref.get('veredicto', '?')
        sello = ('<span class="sello revisado">✔ revisado por un refutador</span>'
                 if v == 'CONFIRMADO' else
                 '<span class="sello parcial">⚠ revisado: parte no sobrevivió</span>')
        detalle = (f'Un segundo equipo volvió a correr los comandos sobre esta sección. '
                   f'<b>Cayeron {cayeron} afirmaciones</b> y encontró <b>{atajos} atajos</b>'
                   + (' — ' + e(' y '.join(cambio)) + '. ' if cambio else '. ')
                   + 'Los números que se publican arriba son <b>los que sobrevivieron</b>, no los que '
                     'había afirmado el primer equipo.')
    else:
        sello = '<span class="sello sinrefutar">◻ todavía sin refutar</span>'
        detalle = ('Este número lo midió un equipo y <b>todavía no lo revisó un segundo</b>. '
                   'En esta casa «verde» es del candado y «hecho» es del refutador: se publica '
                   'diciéndolo, no callándolo. De las ' + _cuantasRefutadas() + ' secciones que sí '
                   'pasaron por un refutador, <b>' + _cuantasConfirmadas() + '</b>.')

    filas = []
    for v in r.get('variables', []):
        npm = nuestroSinMedir(v)
        clase = 'nomedi' if npm else ('bien' if v['hoy'] >= 7.5 else 'medio' if v['hoy'] >= 5 else 'mal')
        valor = 'no pude medir' if npm else coma(v['hoy'])
        lid = 'no pude medir' if liderSinMedir(v) else coma(v['lider'])
        filas.append(f"<tr><th scope='row'>{e(v['nombre'])}</th><td class='{clase}'>{valor}</td>"
                     f"<td class='techo{' nomedi' if liderSinMedir(v) else ''}'>{lid}</td>"
                     f"<td class='denom'>{e(str(v.get('denominador',''))[:160])}"
                     + (f"<br><span class='quienlider'>{e(str(v.get('appLider'))[:200])}</span>"
                        if v.get('appLider') else '')
                     + (f"<br><span class='lam'>lámina Mobbin <code>{e(str(v.get('laminaMobbin'))[:40])}</code>"
                        f"{' · mirada ' + e(str(v.get('fechaMirada'))[:12]) if v.get('fechaMirada') else ''}</span>"
                        if v.get('laminaMobbin') and 'no pude' not in str(v.get('laminaMobbin')).lower() else '')
                     + "</td></tr>")
    arreglos = ''.join(f'<li>{e(str(a))}</li>' for a in r.get('arreglosNuestros', []))
    otros = []
    if r.get('productoNuevo'):
        otros.append('<p class="nota"><b>Producto nuevo que hay que construir</b> — no suma al techo: '
                     + e(' · '.join(map(str, r['productoNuevo']))[:600]) + '</p>')
    if r.get('dependeDeTerceros'):
        otros.append('<p class="nota"><b>Depende de Víctor, de Lucas o de un tercero</b> — tampoco suma: '
                     + e(' · '.join(map(str, r['dependeDeTerceros']))[:600]) + '</p>')
    if r.get('noMedido'):
        otros.append('<p class="nota"><b>Lo que no se pudo medir</b>, y va como 2 y nunca como 0: '
                     + e(' · '.join(map(str, r['noMedido']))[:600]) + '</p>')
    if ref and (ref.get('afirmacionesTumbadas') or ref.get('atajosHallados')):
        caidas = ''.join(f'<li>{e(str(a)[:420])}</li>'
                         for a in (ref.get('afirmacionesTumbadas') or [])[:6])
        atj    = ''.join(f'<li>{e(str(a)[:420])}</li>'
                         for a in (ref.get('atajosHallados') or [])[:5])
        otros.append('<details class="refut"><summary>Qué le tumbó el refutador a este número</summary>'
                     + (f'<p class="nota"><b>Afirmaciones que cayeron</b></p><ol class="arreglos">{caidas}</ol>' if caidas else '')
                     + (f'<p class="nota"><b>Atajos que buscó y encontró</b></p><ol class="arreglos">{atj}</ol>' if atj else '')
                     + '</details>')

    apps = lideres_de(r)
    n = len(r.get('arreglosNuestros', []))
    return (
      '<!--TECHO:INICIO-->'
      f'<p class="puntaje"><b>{coma(hoy)}/10</b> esta sección hoy '
      + (f'<span class="fecha">(media de {_sobre} variables · sin medir de nuestro lado: '
         f'{e(", ".join(_sinMedirNuestro))})</span> ' if _sinMedirNuestro else '')
      + f'· <b>{coma(techo)}</b> '
      f'su techo con sólo código nuestro · medido contra '
      f'{e(" · ".join(apps)) if apps else _sinNombre(r)} '
      f'<span class="fecha">· láminas miradas el 22-sep-2026</span> {sello}</p>\n'
      f'        <p class="nota refnota">{detalle}</p>\n'
      f'        <details class="techo-detalle"><summary>Qué falta para llegar a {coma(techo)} '
      f'— {n} ítem{"s" if n != 1 else ""} de trabajo, todo de código nuestro</summary>\n'
      f'          <div class="techo-cuerpo">\n'
      f'            <div class="tabla-env"><table><thead><tr><th>variable</th><th>hoy</th>'
      f'<th>las líderes</th><th>sobre qué se contó</th></tr></thead>'
      f'<tbody>{"".join(filas)}</tbody></table></div>\n'
      f'            <ol class="arreglos">{arreglos}</ol>\n'
      f'            {"".join(otros)}\n'
      f'            <p class="nota metodo"><b>Cómo salió el número:</b> '
      f'{e(str(r.get("metodo",""))[:900])}</p>\n'
      f'          </div></details><!--TECHO:FIN-->')

doc = open(DOC, encoding='utf-8').read()
# se borra el bloque anterior (puntaje + refnota + details) para no apilar
# 🔴 EL BORRADO DEL BLOQUE ANTERIOR SE HACIA POR FORMA Y SE ROMPIO SOLO.
#    `<p class="puntaje">.*?</details>` cortaba en el PRIMER </details>. El dia
#    que el bloque gano un <details> anidado adentro —el del refutador— el
#    </details> de afuera quedo huerfano, y cada regeneracion sumo uno mas: la
#    version publicada a las 22:27 tenia 3 </details> y 3 </div> de sobra, uno
#    por cada seccion refutada. Ahora el bloque lleva SUS PROPIAS MARCAS y el
#    borrado es por marca: una marca no cambia cuando cambia lo de adentro.
doc = re.sub(r'<!--TECHO:INICIO-->.*?<!--TECHO:FIN-->', '<!--TECHO-->', doc, flags=re.S)

def _sacar_forma_vieja(texto):
    """Saca los bloques `techo-detalle` que se escribieron ANTES de las marcas,
    contando la anidacion en vez de confiar en el primer cierre."""
    salida, i = [], 0
    while True:
        j = texto.find('<details class="techo-detalle">', i)
        if j < 0:
            salida.append(texto[i:]); break
        salida.append(texto[i:j])
        k, hondo = j, 0
        while k < len(texto):
            ab = texto.find('<details', k); ce = texto.find('</details>', k)
            if ce < 0: raise SystemExit('un <details> sin cerrar en el documento')
            if 0 <= ab < ce: hondo += 1; k = ab + 8
            else:
                hondo -= 1; k = ce + 10
                if hondo == 0: break
        i = k
    return ''.join(salida)

doc = _sacar_forma_vieja(doc)
doc = re.sub(r'<p class="puntaje">.*?</p>', '<!--TECHO-->', doc, flags=re.S)
doc = re.sub(r'<p class="nota refnota">.*?</p>', '', doc, flags=re.S)
doc = re.sub(r'<p class="nota" style="margin-top:8px">.*?</p>', '', doc, flags=re.S)

puestas, faltan = [], []
for n in range(1, 16):
    sid = f's{n}'
    m = re.search(r'<section id="' + sid + r'">.*?(<!--TECHO-->)', doc, re.S)
    if not m: faltan.append(sid + ' sin marca'); continue
    if sid not in med: faltan.append(sid + ' sin medición'); continue
    doc = doc[:m.start(1)] + bloque(sid, med[sid]) + doc[m.end(1):]
    puestas.append(sid)

# ── 🔴 NINGUNA RUTA DE LA MAC EN UNA PAGINA PUBLICA ────────────────────────
# Los metodos que escriben los frentes citan el arbol por su ruta absoluta. En
# un documento que se abre sin cuenta eso no le dice nada al lector y si dice
# como esta organizado el disco. Va ACA y no en un comando aparte porque ya
# volvio una vez: un arreglo que hay que acordarse de correr no es un arreglo.
_antes = len(re.findall(r'/Users/cr', doc))
_PARES = [t.split('=', 1) for t in os.environ.get('RAICES_A_TAPAR', '').split(':') if '=' in t]
assert _PARES or _antes == 0, (
    'hay rutas de la Mac en el documento y no me diste RAICES_A_TAPAR')
for _pat, _rep in [(re.escape(a), b) for a, b in _PARES]:
    doc = re.sub(_pat, _rep, doc)
_despues = len(re.findall(r'/Users/cr', doc))
print(f'rutas de la Mac: {_antes} -> {_despues}')
assert _despues == 0, 'quedaron rutas de la Mac'
# control positivo del instrumento: tiene que hallar lo que SI reemplazo
assert 'el repositorio de la app' in doc, 'el reemplazo no dejo rastro: el instrumento no toco nada'

# ── 🔴 EL BALANCE SE COMPRUEBA ACA, NO DESPUES ────────────────────────────
# El documento publicado a las 22:27 salio con 3 </details> y 3 </div> de mas,
# y el control que corri por fuera dijo «ninguno» porque era un parser de
# juguete. Contar aperturas contra cierres no se puede equivocar.
for _t in ('details', 'div', 'section', 'table', 'ol', 'p', 'header', 'article'):
    _a = len(re.findall(r'<' + _t + r'[\s>]', doc))
    _c = len(re.findall(r'</' + _t + r'>', doc))
    assert _a == _c, f'🔴 {_t}: abre {_a} y cierra {_c} ({_a - _c:+d})'
print('balance de etiquetas: 8 familias, todas cerradas')

sobran = doc.count('<!--TECHO-->')
open(DOC, 'w', encoding='utf-8').write(doc)
print('techo propio en:', ' '.join(puestas), f'({len(puestas)} de 15)')
print('con refutador  :', ' '.join(sorted(refut, key=lambda k: int(k[1:]))) or 'ninguna')
print('faltan         :', ' '.join(faltan) or 'ninguna')
print('marcas sin llenar:', sobran)
