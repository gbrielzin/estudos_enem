import { useEffect, useRef } from 'react';
import { Animated, Easing, View } from 'react-native';

export type MascoteMood = 'happy' | 'cheer' | 'sad' | 'sleep';
export type MascotePattern = 'solido' | 'tuxedo' | 'patches';

export interface MascoteProps {
  color?: string;
  shadow?: string;
  /** Nome mantido por compatibilidade (ver docstring) -- não tem mais bico, isto agora tinge o nariz e a parte interna da orelha. */
  beak?: string;
  mood?: MascoteMood;
  size?: number;
  /** Pelagem: 'solido' (padrão) = cor única; 'tuxedo' tinge as orelhas
   * e um "capuz" no topo do corpo com `patch`; 'patches' espalha duas
   * manchas assimétricas de `patch` pelo corpo. Ver docstring da seção
   * "Variações" abaixo pro porquê disso existir. */
  pattern?: MascotePattern;
  /** Cor da mancha/capuz -- só importa quando `pattern` não é 'solido'. */
  patch?: string;
  /** Cor de uma coleira opcional (banda + fivela no pescoço). Sem
   * relação com `pattern` -- pode combinar os dois. */
  collar?: string;
  /** "Pipoco respirando" -- padrão de movimento 6a do projeto de
   * design (Claude Design, App ENEM.dc.html, TURNO 6 "Gramática de
   * animação"): estado parado do mascote em QUALQUER tela, ligado por
   * padrão. Só vale a pena desligar (`animado={false}`) num mascote
   * bem pequeno/inline ao lado de texto (ex: os cards de área de
   * "Montar simulado", 0.33 de tamanho) -- balançar 7px ali chamaria
   * mais atenção do que o próprio texto ao lado. */
  animado?: boolean;
}

/**
 * Mascote "Pipo" -- gatinho branco, porta direta da versão ATUAL de
 * Mascote.dc.html (projeto de design do usuário no Claude Design),
 * substituindo o desenho anterior (um passarinho verde). API do
 * componente sem mudança nenhuma -- mesmas props (`color`/`shadow`/
 * `beak`/`mood`/`size`) que `app/index.tsx`, `app/perfil.tsx` e
 * `components/trilha-path.tsx` já passam, só o VALOR padrão de cada
 * uma mudou pro branco/cinza/rosa do gato -- e essas 3 chamadas agora
 * passam `Brand.branco`/`Brand.brancoEscuro`/`Brand.rosa` em vez de
 * `Brand.verde`/`Brand.ouro` (ver `constants/brand.ts`), pra bater com
 * o novo padrão em vez de depender só do default do componente. `beak`
 * (sem bico agora) virou a cor do nariz + parte interna da orelha --
 * nome da prop mantido de propósito pra não quebrar quem já chama.
 *
 * Sem imagem/arte externa nenhuma, só `View` + estilo, igual o
 * mascote anterior. Duas diferenças reais em relação ao CSS original,
 * confirmadas na documentação oficial do RN antes de escrever isto
 * (reactnative.dev/docs/view-style-props) em vez de assumidas:
 *
 * 1. `border-radius` com valor elíptico por canto ("50% 50% 44% 44% /
 *    56% 56% 44% 44%" no corpo) -- RN só aceita 1 valor por canto
 *    (sem split horizontal/vertical), aproximado com um raio único
 *    por canto (mais arredondado em cima, menos embaixo -- a mesma
 *    intenção visual do valor elíptico original). Mesma limitação e
 *    mesma técnica de aproximação que o mascote anterior já usava.
 * 2. `clip-path: polygon(...)` (orelha triangular, nariz) -- RN não
 *    tem clip-path (confirmado, não existe na doc de View style
 *    props). Recriado com o truque clássico de borda: uma `View` de
 *    0x0 com bordas TRANSPARENTES em dois lados e uma COLORIDA no
 *    terceiro -- RN (como qualquer motor CSS) desenha isso como um
 *    triângulo, técnica padrão pra triângulo sem clip-path/SVG.
 *
 * `boxShadow` (sombra sólida "0 Npx 0 cor", raio de blur zero = sem
 * gradiente nenhum, pedido explícito) É suportado nativamente nesta
 * versão de RN (0.86.3 -- confirmado na doc oficial, spec-compliant
 * com o box-shadow da web, iOS e Android, inset incluso) -- diferente
 * do mascote anterior, que precisou empilhar duas `View`s pra simular
 * isso porque supostamente RN não tinha `boxShadow` (docstring antiga
 * dizia isso; ou ficou desatualizada, ou a versão de RN de então era
 * mais velha -- AGENTS.md deste projeto avisa pra sempre checar a doc
 * da versão atual em vez de reaproveitar suposição antiga, foi
 * exatamente isso que essa checagem evitou aqui). Usado direto no
 * corpo, na cauda e no contorno interno do olho.
 *
 * Variações (`pattern`/`patch`/`collar`) -- pedido explícito do
 * usuário: conforme a matéria/tela muda, o gatinho muda de "roupa"
 * junto (ex: um Pipoco cor de areia com `pattern="patches"` na trilha
 * de uma matéria, um tuxedo cinza na tela de Apresentação -- ver
 * trilha-path.tsx e app/index.tsx). Vem do projeto de design do
 * usuário (Mascote.dc.html, atributos `pattern`/`patch`/`scene` do
 * componente `dc-import`) -- só que `dc-import` é um custom element
 * fechado da própria ferramenta de design, sem HTML/CSS inspecionável
 * por trás, então isto aqui é uma aproximação fiel ao NOME de cada
 * variação (tuxedo = capuz escuro sobre corpo claro, patches = manchas
 * assimétricas), não um pixel-a-pixel do original. `scene` (o terceiro
 * atributo que aparece no design, ex: "estudo"/"fogueira") não virou
 * prop -- é só um nome de contexto pro humano, a aparência real já
 * está inteira em `color`/`pattern`/`patch`.
 */
export function Mascote({
  color = '#FDFEFF',
  shadow = '#C4CFDB',
  beak: nose = '#FF8FA3',
  mood = 'happy',
  size = 1,
  pattern = 'solido',
  patch,
  collar,
  animado = true,
}: MascoteProps) {
  const tilt = mood === 'cheer' ? '-7deg' : mood === 'sad' ? '5deg' : '0deg';

  // "Pipoco respirando" (pk-bob no design): 2,6s em loop, sobe 7px e
  // balança ±1,5° -- valores FIXOS em px/grau, não escalam com `size`
  // (mesma @keyframes do design aplicada igual em qualquer instância).
  // Roda num wrapper RÍGIDO por fora do wrapper de escala (abaixo),
  // pra não interferir no `transformOrigin` que resolve o bug de
  // layout já documentado ali.
  const respirar = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    if (!animado) return;
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(respirar, { toValue: 1, duration: 1300, easing: Easing.inOut(Easing.ease), useNativeDriver: false }),
        Animated.timing(respirar, { toValue: 0, duration: 1300, easing: Easing.inOut(Easing.ease), useNativeDriver: false }),
      ]),
    );
    loop.start();
    return () => loop.stop();
  }, [animado, respirar]);
  const respirarY = respirar.interpolate({ inputRange: [0, 1], outputRange: [0, -7] });
  const respirarRotacao = respirar.interpolate({ inputRange: [0, 1], outputRange: ['-1.5deg', '1.5deg'] });
  const pupilY = mood === 'sad' ? 4 : mood === 'cheer' ? -2 : 0;
  const pupilWidth = mood === 'cheer' ? 12 : 9.5;
  const fechado = mood === 'sleep' || mood === 'sad';
  const alturaPalpebra = mood === 'sleep' ? 17 : 14;
  const earTilt = mood === 'sad' ? 32 : mood === 'cheer' ? -4 : 7;
  const tailTop = mood === 'cheer' ? 40 : 62;
  const tailRotate = mood === 'cheer' ? '-54deg' : '-16deg';
  const corOrelha = pattern === 'tuxedo' && patch ? patch : color;

  // Wrapper externo com o tamanho VISUAL de verdade (104*size) -- por
  // dentro, o View de 104x104 nativo (todo o resto deste componente usa
  // offsets em px pensados pra essa referência) só encolhe visualmente
  // via transform:scale, que em React Native (igual em CSS web, mesmo
  // bug já achado e corrigido em ui_theme.mascote_html() no lado
  // Streamlit) NUNCA muda o espaço reservado em layout, só o que é
  // pintado na tela. Sem este wrapper, um <Mascote size={0.33}/> dentro
  // de uma linha flexDirection:'row' (como os cards de área da tela
  // "Montar simulado") reservava 104px de largura mesmo aparentando
  // ser bem menor -- sobrava pouco espaço de verdade pro texto vizinho,
  // que quebrava letra por letra ("Natu/reza", "Mate/máti/ca"), achado
  // ao vivo no navegador. `transformOrigin: 'top left'` (em vez do
  // padrão "center") é o que faz o conteúdo encolhido bater exatamente
  // com o canto (0,0) do wrapper, em vez de encolher pro centro e
  // sobrar espaço torto.
  return (
    <Animated.View
      style={{
        width: 104 * size,
        height: 104 * size,
        transform: animado ? [{ translateY: respirarY }, { rotate: respirarRotacao }] : undefined,
      }}>
    <View style={{ width: 104, height: 104, transform: [{ scale: size }, { rotate: tilt }], transformOrigin: 'top left' }}>
      {/* cauda -- pill rotacionado, sombra sólida via boxShadow (nunca gradiente) */}
      <View
        style={{
          position: 'absolute', right: -18, top: tailTop, width: 46, height: 13, borderRadius: 999,
          backgroundColor: color, boxShadow: `0 3px 0 ${shadow}`,
          transform: [{ rotate: tailRotate }], transformOrigin: 'left center',
        }}
      />

      {/* orelhas triangulares (truque de borda, ver docstring) -- tuxedo
          tinge a orelha inteira com `patch` (o "capuz" continua até a
          ponta da orelha), patches deixa a orelha na cor base. */}
      <Orelha lado="left" tilt={earTilt} color={corOrelha} nose={nose} />
      <Orelha lado="right" tilt={earTilt} color={corOrelha} nose={nose} />

      {/* corpo -- 88x84, raio aproximado do valor elíptico original, sombra sólida embaixo */}
      <View
        style={{
          position: 'absolute', left: 8, top: 14, width: 88, height: 84,
          borderTopLeftRadius: 46, borderTopRightRadius: 46,
          borderBottomLeftRadius: 39, borderBottomRightRadius: 39,
          backgroundColor: color, boxShadow: `0 8px 0 ${shadow}`, overflow: 'hidden',
        }}>
        {pattern === 'tuxedo' && patch && (
          // "Capuz": cobre só o terço de cima do corpo, mesmo raio do
          // corpo em cima -- lê como uma pelagem escura na cabeça/costas
          // sobre um corpo claro, sem precisar de clip-path (RN não tem).
          <View style={{ position: 'absolute', left: 0, top: 0, right: 0, height: 32, backgroundColor: patch, borderTopLeftRadius: 46, borderTopRightRadius: 46 }} />
        )}
        {pattern === 'patches' && patch && (
          <>
            <View style={{ position: 'absolute', left: -6, top: -4, width: 34, height: 30, borderRadius: 16, backgroundColor: patch, transform: [{ rotate: '-12deg' }] }} />
            <View style={{ position: 'absolute', right: -8, bottom: -6, width: 30, height: 26, borderRadius: 14, backgroundColor: patch, transform: [{ rotate: '10deg' }] }} />
          </>
        )}
        <View style={{ position: 'absolute', left: 18, top: 26, width: 52, height: 38, borderRadius: 26, backgroundColor: 'rgba(255,255,255,0.5)' }} />
      </View>

      {collar && (
        // Coleira -- banda + fivela, INDEPENDENTE de pattern (não fica
        // clipada pelo overflow do corpo, fica por cima, no colo).
        <View style={{ position: 'absolute', left: 22, top: 60, width: 60, height: 11, borderRadius: 6, backgroundColor: collar, zIndex: 2 }}>
          <View style={{ position: 'absolute', left: '50%', top: 1.5, marginLeft: -4, width: 8, height: 8, borderRadius: 4, backgroundColor: 'rgba(255,255,255,0.85)' }} />
        </View>
      )}

      {/* olhos -- contorno via boxShadow inset em vez de borda dupla */}
      <Olho lado="left" fechado={fechado} pupilY={pupilY} pupilWidth={pupilWidth} corPalpebra={color} corSombraPalpebra={shadow} alturaPalpebra={alturaPalpebra} />
      <Olho lado="right" fechado={fechado} pupilY={pupilY} pupilWidth={pupilWidth} corPalpebra={color} corSombraPalpebra={shadow} alturaPalpebra={alturaPalpebra} />

      {/* bigodes -- 3 de cada lado, leque de ângulos */}
      <Bigode lado="left" indice={0} cor={shadow} />
      <Bigode lado="left" indice={1} cor={shadow} />
      <Bigode lado="left" indice={2} cor={shadow} />
      <Bigode lado="right" indice={0} cor={shadow} />
      <Bigode lado="right" indice={1} cor={shadow} />
      <Bigode lado="right" indice={2} cor={shadow} />

      {/* nariz -- triângulo pra baixo (truque de borda) */}
      <View
        style={{
          position: 'absolute', left: '50%', top: 63, marginLeft: -7.5,
          width: 0, height: 0,
          borderLeftWidth: 7.5, borderRightWidth: 7.5, borderTopWidth: 11,
          borderLeftColor: 'transparent', borderRightColor: 'transparent', borderTopColor: nose,
        }}
      />

      {/* boca -- sorriso cheio (cheer) ou contorno em U (resto) */}
      {mood === 'cheer' ? (
        <View
          style={{
            position: 'absolute', left: '50%', top: 75, marginLeft: -10.5, width: 21, height: 15,
            borderBottomLeftRadius: 999, borderBottomRightRadius: 999, backgroundColor: '#8C3448',
          }}
        />
      ) : (
        <View
          style={{
            position: 'absolute', left: '50%', top: 74, marginLeft: -9.5, width: 19, height: 9,
            borderBottomLeftRadius: 999, borderBottomRightRadius: 999,
            borderWidth: 2.5, borderTopWidth: 0, borderColor: shadow, backgroundColor: 'transparent',
          }}
        />
      )}

      {/* bochechas */}
      <View style={{ position: 'absolute', left: 11, top: 70, width: 15, height: 9, borderRadius: 7.5, backgroundColor: 'rgba(255,143,163,0.5)' }} />
      <View style={{ position: 'absolute', right: 11, top: 70, width: 15, height: 9, borderRadius: 7.5, backgroundColor: 'rgba(255,143,163,0.5)' }} />

      {/* brilho de comemoração */}
      {mood === 'cheer' && (
        <View style={{ position: 'absolute', left: -10, top: -6, width: 15, height: 15, transform: [{ rotate: '45deg' }], borderRadius: 4, backgroundColor: '#FFC42E' }} />
      )}
    </View>
    </Animated.View>
  );
}

function Orelha({ lado, tilt, color, nose }: { lado: 'left' | 'right'; tilt: number; color: string; nose: string }) {
  const rot = lado === 'left' ? -tilt : tilt;
  return (
    <View
      style={{
        position: 'absolute', [lado]: 8, top: 0, width: 33, height: 35,
        transform: [{ rotate: `${rot}deg` }], transformOrigin: 'center bottom',
      }}>
      {/* triângulo branco (orelha) */}
      <View
        style={{
          width: 0, height: 0,
          borderLeftWidth: 16.5, borderRightWidth: 16.5, borderBottomWidth: 35,
          borderLeftColor: 'transparent', borderRightColor: 'transparent', borderBottomColor: color,
        }}
      />
      {/* triângulo rosa (parte interna) */}
      <View
        style={{
          position: 'absolute', left: 9.5, top: 13, opacity: 0.8,
          width: 0, height: 0,
          borderLeftWidth: 7, borderRightWidth: 7, borderBottomWidth: 18,
          borderLeftColor: 'transparent', borderRightColor: 'transparent', borderBottomColor: nose,
        }}
      />
    </View>
  );
}

function Olho({
  lado,
  fechado,
  pupilY,
  pupilWidth,
  corPalpebra,
  corSombraPalpebra,
  alturaPalpebra,
}: {
  lado: 'left' | 'right';
  fechado: boolean;
  pupilY: number;
  pupilWidth: number;
  corPalpebra: string;
  corSombraPalpebra: string;
  alturaPalpebra: number;
}) {
  return (
    <View
      style={{
        position: 'absolute', [lado]: 17, top: 34, width: 27, height: 27, borderRadius: 13.5,
        backgroundColor: '#F4F7FA', alignItems: 'center', justifyContent: 'center', overflow: 'hidden',
        boxShadow: `inset 0 0 0 1.5px ${corSombraPalpebra}`,
      }}>
      <View
        style={{
          width: pupilWidth, height: 18, borderRadius: pupilWidth / 2,
          backgroundColor: '#141821', transform: [{ translateY: pupilY }],
        }}
      />
      {fechado && (
        <View
          style={{
            position: 'absolute', left: 0, top: 0, width: 27, height: alturaPalpebra,
            backgroundColor: corPalpebra, borderBottomWidth: 2.5, borderBottomColor: corSombraPalpebra,
          }}
        />
      )}
    </View>
  );
}

function Bigode({ lado, indice, cor }: { lado: 'left' | 'right'; indice: 0 | 1 | 2; cor: string }) {
  const anguloBase = indice === 0 ? 13 : indice === 1 ? 0 : -13;
  const rot = (lado === 'left' ? 1 : -1) * anguloBase;
  return (
    <View
      style={{
        position: 'absolute', [lado]: -8, top: 63 + indice * 8, width: 28, height: 2.5, borderRadius: 999,
        backgroundColor: cor, transform: [{ rotate: `${rot}deg` }],
      }}
    />
  );
}
