import { Feather } from '@expo/vector-icons';
import { useEffect, useState } from 'react';
import { Animated, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { Mascote } from '@/components/mascote';
import { Brand, Fontes, RaioCard } from '@/constants/brand';
import { interpolarSombraBotao, useInteracaoBotao } from '@/hooks/use-interacao-botao';
import { ResumoGeral, getResumoGeral } from '@/lib/api';

/**
 * "Seu bilhete" -- 2a tela do fluxo "TURNO 5 — SIMULADO NO CELULAR" do
 * mockup (App ENEM.dc.html, importado ao vivo via DesignSync,
 * 2026-09-11), aberta a partir do botão "Emitir bilhete" em
 * app/simulado.tsx.
 *
 * NÃO é uma rota de expo-router (não mora em app/, é um componente
 * comum) -- tentei registrar como rota de verdade primeiro (arquivo
 * em app/bilhete.tsx + <TabTrigger> escondido em components/app-
 * tabs.tsx), mas o sistema de Tabs customizado deste app (expo-router/
 * ui, ver comentário grande em app-tabs.tsx) despacha troca de tela
 * via `JUMP_TO` de navegação nativa, e esse JUMP_TO nunca foi
 * reconhecido pelo navigator de verdade ("The action 'JUMP_TO' with
 * payload... was not handled by any navigator", erro visto ao vivo no
 * console mesmo com o TabTrigger registrado igual aos outros 6).
 * Trocado pelo MESMO padrão que app/index.tsx já usa pra Apresentação
 * ↔ Trilha ↔ Exercício: alternar "fase" com state local
 * (simulado.tsx guarda `fase` e passa `onVoltar`), sem navegação de
 * verdade nenhuma -- mais simples e já comprovado funcionando neste
 * app, em vez de brigar com a API interna do Tabs por uma tela que
 * nem precisa de URL própria.
 *
 * `ano`/`area`/`modo` vêm por PROPS de simulado.tsx (o que foi
 * escolhido em "Montar simulado"), nenhum dado novo inventado. "Nº
 * [código]" usa o mesmo truque do lado Streamlit
 * (resumo_geral_desempenho().total_tentativas, ver _renderizar_montar_
 * prova em cartao_resposta.py) só pra não ser um número 100% fixo à
 * toa. O resto ("Modo prova liga o silencioso...", "Pode pausar 2
 * vezes...", "Sem sinal?...", a fala do Pipoco) é texto ESTÁTICO,
 * cópia fiel do mockup -- nenhum desses 3 avisos tem lógica de verdade
 * por trás ainda (silencioso automático, pausa contável, download
 * offline), são só o clima da tela por enquanto, mesmo espírito "só
 * visualmente, depois a lógica" já usado nas telas anteriores. O botão
 * "Destacar e entrar" ainda não faz nada -- a prova em si (responder
 * questão por questão no celular) é a PRÓXIMA interface, fora do
 * escopo desta rodada.
 */
const ROTULO_AREA: Record<string, string> = {
  natureza: 'Ciências da Natureza',
  matematica: 'Matemática',
  humanas: 'Ciências Humanas',
  linguagens: 'Linguagens',
  ambas: 'Matemática + Natureza',
};
const ROTULO_MODO: Record<string, string> = {
  cronometro: 'Com cronômetro',
  livre: 'Sem pressa',
  resolvendo: 'Corrige a cada questão',
};

export function TelaBilhete({
  ano,
  area,
  modo,
  onVoltar,
}: {
  ano: number;
  area: string;
  modo: string;
  onVoltar: () => void;
}) {
  const nQuestoes = area === 'ambas' ? 90 : 45;
  const tempo = area === 'ambas' ? '3h' : '1h30';

  const [resumo, setResumo] = useState<ResumoGeral | null>(null);
  useEffect(() => {
    getResumoGeral().then(setResumo).catch(() => {});
  }, []);
  const numeroBilhete = String(((resumo?.total_tentativas ?? 0) % 900) + 100).padStart(4, '0');
  const destacar = useInteracaoBotao();
  const destacarSombra = interpolarSombraBotao(destacar.deslocamentoY, Brand.ouroEscuro);

  return (
    <>
      <ScrollView style={styles.scrollFlex} contentContainerStyle={styles.scroll}>
        <View style={styles.cabecalho}>
          <Pressable style={styles.voltarBtn} onPress={onVoltar}>
            <Feather name="chevron-left" size={20} color={Brand.texto} />
          </Pressable>
          <Text style={styles.titulo}>Seu bilhete</Text>
          <View style={styles.numeroBadge}>
            <Text style={styles.numeroBadgeTexto}>Nº {numeroBilhete}</Text>
          </View>
        </View>

        <View style={styles.ticket}>
          <View style={styles.ticketHeader}>
            <Mascote mood="cheer" collar={Brand.ouro} size={0.46} />
            <View style={{ flex: 1, minWidth: 0 }}>
              <Text style={styles.ticketKicker}>ENEM · CADERNO AZUL</Text>
              <Text style={styles.ticketArea}>{ROTULO_AREA[area] ?? area}</Text>
            </View>
          </View>
          <View style={styles.ticketCorpo}>
            <View style={styles.ticketLinha}>
              <View style={styles.ticketCampo}>
                <Text style={styles.ticketCampoLabel}>ANO</Text>
                <Text style={styles.ticketCampoValor}>{ano}</Text>
              </View>
              <View style={styles.ticketCampo}>
                <Text style={styles.ticketCampoLabel}>QUESTÕES</Text>
                <Text style={styles.ticketCampoValor}>{nQuestoes}</Text>
              </View>
              <View style={styles.ticketCampo}>
                <Text style={styles.ticketCampoLabel}>TEMPO</Text>
                <Text style={styles.ticketCampoValor}>{tempo}</Text>
              </View>
            </View>
            <View style={styles.ticketDivisor} />
            <View style={styles.ticketLinha}>
              <View style={styles.ticketCampo}>
                <Text style={styles.ticketCampoLabel}>MODO</Text>
                <Text style={styles.ticketCampoModo}>{ROTULO_MODO[modo] ?? modo}</Text>
              </View>
              <View style={styles.codigoBarras}>
                {[3, 2, 5, 2, 3, 6, 2, 4, 2, 5].map((w, i) => (
                  <View key={i} style={{ width: w, height: 28, backgroundColor: '#131722' }} />
                ))}
              </View>
            </View>
          </View>
        </View>

        <View style={styles.secao}>
          <Text style={styles.rotuloSecao}>ANTES DE COMEÇAR</Text>
          <View style={styles.avisoRow}>
            <Feather name="check" size={18} color={Brand.verde} />
            <Text style={styles.avisoTexto}>Modo prova liga o silencioso e esconde as notificações</Text>
          </View>
          <View style={styles.avisoRow}>
            <Feather name="clock" size={18} color={Brand.ouro} />
            <Text style={styles.avisoTexto}>Pode pausar 2 vezes. O relógio para junto</Text>
          </View>
          <View style={styles.avisoRow}>
            <Feather name="download" size={18} color={Brand.roxo} />
            <Text style={styles.avisoTexto}>Sem sinal? Baixa antes e corrige depois</Text>
          </View>
        </View>

        <View style={styles.pipocoRow}>
          <Mascote mood="happy" collar={Brand.verde} size={0.62} />
          <View style={styles.balaoFala}>
            <Text style={styles.balaoTexto}>
              Tô com o caderno aberto. Quando você destacar o bilhete eu começo a contar.
            </Text>
          </View>
        </View>
      </ScrollView>

      <View style={styles.rodape}>
        <Pressable {...destacar.handlers}>
          <Animated.View
            style={[
              styles.destacarBtn,
              { boxShadow: destacarSombra, transform: [{ translateY: destacar.deslocamentoY }] },
            ]}>
            <Text style={styles.destacarBtnTexto}>Destacar e entrar</Text>
          </Animated.View>
        </Pressable>
      </View>
    </>
  );
}

const styles = StyleSheet.create({
  scrollFlex: { flex: 1, minHeight: 0 },
  scroll: { padding: 16, paddingBottom: 24, gap: 22 },
  cabecalho: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  voltarBtn: {
    width: 40,
    height: 40,
    borderRadius: 13,
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    alignItems: 'center',
    justifyContent: 'center',
  },
  titulo: {
    flex: 1,
    fontFamily: Fontes.titulo,
    fontSize: 19,
    lineHeight: 22,
    color: Brand.texto,
  },
  numeroBadge: {
    backgroundColor: Brand.ouro,
    borderRadius: 8,
    paddingHorizontal: 9,
    paddingVertical: 5,
  },
  numeroBadgeTexto: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 11,
    color: '#150F2B',
  },
  ticket: {
    backgroundColor: '#F2F4F7',
    borderRadius: RaioCard,
    overflow: 'hidden',
  },
  ticketHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    backgroundColor: Brand.roxo,
    paddingVertical: 16,
    paddingHorizontal: 18,
  },
  ticketKicker: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 10.5,
    letterSpacing: 1.2,
    color: Brand.roxoClaro,
  },
  ticketArea: {
    fontFamily: Fontes.titulo,
    fontSize: 19,
    lineHeight: 22,
    color: '#FFFFFF',
  },
  ticketCorpo: {
    padding: 18,
    gap: 13,
  },
  ticketLinha: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 14,
  },
  ticketCampo: { flex: 1, gap: 2 },
  ticketCampoLabel: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 10,
    letterSpacing: 1,
    color: '#7A8494',
  },
  ticketCampoValor: {
    fontFamily: Fontes.titulo,
    fontSize: 26,
    lineHeight: 30,
    color: '#131722',
  },
  ticketCampoModo: {
    fontFamily: Fontes.titulo,
    fontSize: 14,
    lineHeight: 17,
    color: '#131722',
  },
  ticketDivisor: {
    height: 2,
    borderRadius: 1,
    backgroundColor: '#D8DEE7',
  },
  codigoBarras: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 2.5,
  },
  secao: { gap: 9 },
  rotuloSecao: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 11,
    letterSpacing: 1.2,
    color: Brand.textoSuave,
  },
  avisoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    backgroundColor: Brand.bgCard,
    borderWidth: 1.5,
    borderColor: Brand.borda,
    borderRadius: 16,
    padding: 13,
  },
  avisoTexto: {
    flex: 1,
    fontFamily: Fontes.corpoNegrito,
    fontSize: 13,
    lineHeight: 18,
    color: Brand.brancoEscuro,
  },
  pipocoRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 10,
  },
  balaoFala: {
    flex: 1,
    minWidth: 0,
    backgroundColor: Brand.bgCardEscuro,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderRadius: 16,
    borderBottomLeftRadius: 5,
    padding: 12,
  },
  balaoTexto: {
    fontFamily: Fontes.corpo,
    fontSize: 12.5,
    lineHeight: 18,
    color: Brand.textoSuave,
  },
  rodape: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: Brand.borda,
  },
  destacarBtn: {
    backgroundColor: Brand.ouro,
    borderRadius: 18,
    paddingVertical: 16,
    alignItems: 'center',
  },
  destacarBtnTexto: {
    fontFamily: Fontes.titulo,
    fontSize: 17,
    lineHeight: 20,
    color: '#3D2C00',
  },
});
