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
import json, re, html

SCR = '(scratchpad)'
DOC = 'este documento'
med    = json.load(open(f'{SCR}/mediciones.json', encoding='utf-8'))
try:    refut = json.load(open(f'{SCR}/refutaciones.json', encoding='utf-8'))
except: refut = {}

med.setdefault('s11', json.load(open(f'{SCR}/s11.json', encoding='utf-8')))

def coma(x):
    try: return f'{float(x):.2f}'.replace('.', ',')
    except Exception: return '—'

def lideres_de(r):
    apps = []
    for v in r.get('variables', []):
        a = (v.get('appLider') or '').strip()
        if a and a not in apps: apps.append(a)
    return (apps or r.get('lideres', []))[:6]

def bloque(sid, r):
    e = html.escape
    ref   = refut.get(sid)
    hoy   = r.get('hoy', r.get('hoyRederivado'))
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
                   'diciéndolo, no callándolo. De las secciones ya revisadas, las tres bajaron.')

    filas = []
    for v in r.get('variables', []):
        npm = v.get('noPudeMedir')
        clase = 'nomedi' if npm else ('bien' if v['hoy'] >= 7.5 else 'medio' if v['hoy'] >= 5 else 'mal')
        valor = 'no pude medir' if npm else coma(v['hoy'])
        filas.append(f"<tr><th scope='row'>{e(v['nombre'])}</th><td class='{clase}'>{valor}</td>"
                     f"<td class='techo'>{coma(v.get('lider', 0))}</td>"
                     f"<td class='denom'>{e(str(v.get('denominador',''))[:160])}</td></tr>")
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
      f'<p class="puntaje"><b>{coma(hoy)}/10</b> esta sección hoy · <b>{coma(techo)}</b> '
      f'su techo con sólo código nuestro · medido contra '
      f'{e(" · ".join(apps)) if apps else "las líderes de este momento de uso"} '
      f'<span class="fecha">· láminas miradas el 22-sep-2026</span> {sello}</p>\n'
      f'        <p class="nota refnota">{detalle}</p>\n'
      f'        <details class="techo-detalle"><summary>Qué falta para llegar a {coma(techo)} '
      f'— {n} arreglo{"s" if n != 1 else ""}, todos de código nuestro</summary>\n'
      f'          <div class="techo-cuerpo">\n'
      f'            <div class="tabla-env"><table><thead><tr><th>variable</th><th>hoy</th>'
      f'<th>las líderes</th><th>sobre qué se contó</th></tr></thead>'
      f'<tbody>{"".join(filas)}</tbody></table></div>\n'
      f'            <ol class="arreglos">{arreglos}</ol>\n'
      f'            {"".join(otros)}\n'
      f'            <p class="nota metodo"><b>Cómo salió el número:</b> '
      f'{e(str(r.get("metodo",""))[:900])}</p>\n'
      f'          </div></details>')

doc = open(DOC, encoding='utf-8').read()
# se borra el bloque anterior (puntaje + refnota + details) para no apilar
doc = re.sub(r'<p class="puntaje">.*?</details>', '<!--TECHO-->', doc, flags=re.S)
doc = re.sub(r'<p class="puntaje">.*?</p>\s*<p class="nota" style="margin-top:8px">.*?</p>',
             '<!--TECHO-->', doc, flags=re.S)
doc = re.sub(r'<p class="puntaje">.*?</p>', '<!--TECHO-->', doc, flags=re.S)

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
for _pat, _rep in [
    (r'el repositorio de este documento/la-super-app/index\.html', 'este documento'),
    (r'el repositorio de este documento', 'el repositorio de este documento'),
    (r'el repositorio de la app', 'el repositorio de la app'),
    (r'los entregables/', 'los entregables/'),
    (r'', ''), (r'', ''),
]:
    doc = re.sub(_pat, _rep, doc)
_despues = len(re.findall(r'/Users/cr', doc))
print(f'rutas de la Mac: {_antes} -> {_despues}')
assert _despues == 0, 'quedaron rutas de la Mac'
# control positivo del instrumento: tiene que hallar lo que SI reemplazo
assert 'el repositorio de la app' in doc, 'el reemplazo no dejo rastro: el instrumento no toco nada'

sobran = doc.count('<!--TECHO-->')
open(DOC, 'w', encoding='utf-8').write(doc)
print('techo propio en:', ' '.join(puestas), f'({len(puestas)} de 15)')
print('con refutador  :', ' '.join(sorted(refut, key=lambda k: int(k[1:]))) or 'ninguna')
print('faltan         :', ' '.join(faltan) or 'ninguna')
print('marcas sin llenar:', sobran)
