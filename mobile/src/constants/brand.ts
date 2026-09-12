/**
 * Paleta e tokens visuais do app mobile -- valores exatos do arquivo
 * de design "App ENEM.dc.html" (Claude Design, projeto do usuário,
 * variante "1a — Grafite & Lima": lima como ação, violeta como
 * progresso, âmbar como recompensa). Importado via DesignSync
 * (projectId 669f9530-e4b9-4dfb-ab2c-cd90df9199b4) -- ver Mascote.dc.html
 * pro componente do mascote "Pipo" (mobile/src/components/mascote.tsx).
 *
 * Isso é a segunda substituição da paleta (a primeira tinha vindo do
 * mockup HTML solto de uma conversa anterior) -- esta é a fonte da
 * verdade agora porque veio do projeto de design de verdade do
 * usuário, não de um rascunho de conversa.
 */
export const Brand = {
  bg: '#0A0C10',
  bgCard: '#171B24',
  bgCardEscuro: '#12151C',
  borda: '#232733',
  bordaForte: '#2C3342',

  texto: '#F2F4F7',
  textoSuave: '#7C8494',
  textoApagado: '#5B6472',
  textoMuted: '#4B5364',

  roxo: '#7C5CFF',
  roxoEscuro: '#4E33C4',
  roxoClaro: '#F1EEFF',
  roxoBg: '#241A3A',

  // Painel roxo-escuro do card "Apresentação" da trilha (ver
  // resumos-trilha.ts) -- tom mais fechado que roxoBg, importado do
  // mesmo projeto de design, tela "Apresentação".
  roxoBgEscuro: '#1A1533',
  roxoBordaEscura: '#3B2E77',
  roxoTextoEscuro: '#A594FF',
  roxoTextoSuave: '#B8AEE8',

  verde: '#6EE12B',
  verdeEscuro: '#3F8F14',
  verdeClaro: '#EAFBDD',

  ouro: '#FFC42E',
  ouroEscuro: '#8A6300',
  ouroBg: '#2A2210',
  ouroBorda: '#4A3B10',

  // Gatinho branco do mascote (ver Mascote.dc.html/mascote.tsx) -- não
  // é a paleta de marca do resto do app (lima/violeta/âmbar), é a cor
  // própria do bichinho, mas mora aqui pelo mesmo motivo de tudo
  // acima: fonte única, os 3 lugares que renderizam <Mascote> (app/
  // index.tsx, app/perfil.tsx, trilha-path.tsx) referenciam daqui em
  // vez de repetir hex solto.
  branco: '#FDFEFF',
  brancoEscuro: '#C4CFDB',
  rosa: '#FF8FA3',

  // Variações de pelagem (Mascote pattern="tuxedo"/"patches", ver
  // mascote.tsx) -- cada uma amarrada a um contexto/tela específico do
  // projeto de design, não a uma matéria ainda (só Óptica tem conteúdo
  // por enquanto pra justificar variação por matéria de verdade -- ver
  // constants/resumos-trilha.ts). "areia" é o Pipoco da trilha (tela
  // Trilha, "cena fogueira" do design); "tuxedoMancha" é só a cor da
  // mancha do Pipoco de tuxedo da tela Apresentação, corpo continua
  // branco (`branco`/`brancoEscuro` acima).
  gatoAreia: '#F5C98A',
  gatoAreiaSombra: '#C99A5B',
  gatoAreiaMancha: '#E0A05C',
  mascoteTuxedoMancha: '#3A4152',

  azul: '#4FA6FF',
  azulBg: '#12233A',
  teal: '#3ED9B0',
  tealBg: '#0F241F',
  laranja: '#FF6B4A',
  laranjaEscuro: '#C33F22',
  laranjaBg: '#3A1F14',

  erro: '#FF6B4A',
} as const;

/** Baloo 2 pra títulos/rótulos com peso (o "tom brincalhão" do
 * mockup); Nunito pro resto do texto corrido. Carregadas via
 * @expo-google-fonts em app/_layout.tsx. */
export const Fontes = {
  titulo: 'Baloo2_800ExtraBold',
  tituloSemibold: 'Baloo2_700Bold',
  corpo: 'Nunito_400Regular',
  corpoNegrito: 'Nunito_700Bold',
  corpoExtraNegrito: 'Nunito_800ExtraBold',
} as const;

export const RaioCard = 22;
