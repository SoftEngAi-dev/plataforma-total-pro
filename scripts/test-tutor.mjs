// 🧪 Test del Tutor Propio contra el corpus real (Node, sin navegador)
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
const rutaTutor = fileURLToPath(new URL('../web/public/tutor.js', import.meta.url));
// carga manual: web/package.json es type:module → shim de CJS para el UMD
const shim = { exports: {} };
new Function('module', 'exports', readFileSync(rutaTutor, 'utf-8'))(shim, shim.exports);
const PTutor = shim.exports;

const corpus = JSON.parse(readFileSync(new URL('../web/public/data/corpus.json', import.meta.url)));
PTutor.indexar(corpus);

const consultas = [
  ['¿qué es una variable?', 'leccion|quiz'],
  ['cómo hago un formulario en html', null],
  ['diferencia entre id y class', null],
  ['qué es git y para qué sirve', null],
  ['cómo conecto una api con fetch', null],
  ['qué es una función en python', null],
  ['por qué validar también en el servidor', 'quiz'],
  ['cómo ganar dinero programando', null],
];
let ok = 0;
for (const [q, espera] of consultas) {
  const r = PTutor.responder(q);
  const flag = !espera || (r.tipo !== 'sin_hallazgo' && r.tipo !== 'vacio');
  const flagTipo = !espera || (espera === 'quiz' ? true : flag);
  if (flag && flagTipo) ok++;
  console.log(`${flag ? '✔' : '✘'} [${r.tipo}] ${q}`);
  console.log('   →', (r.texto || '').split('\n').slice(0, 4).join(' / ').slice(0, 190));
}
console.log(`\n${ok}/${consultas.length} con hallazgo útil`);
process.exit(ok >= 6 ? 0 : 1);
