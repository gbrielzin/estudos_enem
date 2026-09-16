import { Feather, Ionicons } from '@expo/vector-icons';
import { StyleSheet, Text, View } from 'react-native';

import { Brand, Fontes, RaioCard } from '@/constants/brand';
import { NoTrilha, NoTrilhaFixa } from '@/lib/api';

import { TrilhaPath } from './trilha-path';

interface TrilhaFixaPathProps {
  trilhaFixa: NoTrilhaFixa[];
  onAbrirNo: (no: NoTrilha) => void;
}

/**
 * Trilha fixa entrelaçada entre matérias (ver db.trilha_fixa() em
 * core/db.py, ordem de ROI em docs/arquitetura_questoes/arquitetura-
 * trilha.docx) -- visual espelha o mockup "Trilha fixa" do Claude
 * Design (App ENEM.dc.html, TURNO 5): matéria concluída colapsa num
 * resumo compacto, a matéria ativa mostra a trilha de nós normal
 * (reaproveitando TrilhaPath -- mesmo componente da trilha de matéria
 * única, só que uma seção por vez), e as matérias ainda bloqueadas
 * aparecem como um cartão travado no fim, sem revelar os nós.
 */
export function TrilhaFixaPath({ trilhaFixa, onAbrirNo }: TrilhaFixaPathProps) {
  return (
    <View style={styles.container}>
      {trilhaFixa.map((no) => {
        if (no.concluido) {
          return <SecaoConcluida key={no.chave} no={no} />;
        }
        if (no.desbloqueado) {
          return (
            <View key={no.chave} style={styles.secaoAtiva}>
              <BannerMateriaAtiva no={no} />
              <TrilhaPath trilha={no.blocos} onAbrirNo={onAbrirNo} />
            </View>
          );
        }
        return <SecaoBloqueada key={no.chave} no={no} />;
      })}
    </View>
  );
}

function SecaoConcluida({ no }: { no: NoTrilhaFixa }) {
  const total = no.blocos.reduce((soma, b) => soma + b.questoes.length, 0);
  return (
    <View style={styles.cardConcluido}>
      <View style={styles.cardConcluidoIcone}>
        <Ionicons name="checkmark" size={18} color="#0D2705" />
      </View>
      <View style={styles.cardConcluidoTextos}>
        <Text style={styles.rotuloApagado}>CONCLUÍDA</Text>
        <Text style={styles.cardConcluidoTitulo}>{no.nome}</Text>
      </View>
      <Text style={styles.cardConcluidoContagem}>{total}/{total}</Text>
    </View>
  );
}

function BannerMateriaAtiva({ no }: { no: NoTrilhaFixa }) {
  const totalBlocos = no.blocos.length;
  const blocosConcluidos = no.blocos.filter((b) => b.concluido).length;
  return (
    <View style={styles.bannerAtivo}>
      <View style={styles.bannerAtivoTextos}>
        <Text style={styles.bannerAtivoRotulo}>CIÊNCIAS DA NATUREZA</Text>
        <Text style={styles.bannerAtivoTitulo}>{no.nome}</Text>
        <Text style={styles.bannerAtivoProgresso}>
          {blocosConcluidos} de {totalBlocos} nó(s)
        </Text>
      </View>
    </View>
  );
}

function SecaoBloqueada({ no }: { no: NoTrilhaFixa }) {
  return (
    <View style={styles.cardBloqueado}>
      <View style={styles.cardBloqueadoIcone}>
        <Feather name="lock" size={17} color={Brand.textoMuted} />
      </View>
      <View style={styles.cardBloqueadoTextos}>
        <Text style={styles.cardBloqueadoTitulo}>{no.nome}</Text>
        <Text style={styles.cardBloqueadoSubtitulo}>Libera ao concluir a matéria anterior</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    gap: 14,
  },
  secaoAtiva: {
    gap: 4,
  },
  cardConcluido: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderRadius: RaioCard,
    padding: 14,
  },
  cardConcluidoIcone: {
    width: 34,
    height: 34,
    borderRadius: 17,
    backgroundColor: Brand.verde,
    justifyContent: 'center',
    alignItems: 'center',
  },
  cardConcluidoTextos: {
    flex: 1,
    gap: 2,
  },
  rotuloApagado: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 10.5,
    letterSpacing: 1,
    color: Brand.textoApagado,
  },
  cardConcluidoTitulo: {
    fontFamily: Fontes.titulo,
    fontSize: 15,
    color: Brand.textoSuave,
  },
  cardConcluidoContagem: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 13,
    color: Brand.verde,
  },
  bannerAtivo: {
    backgroundColor: Brand.verde,
    boxShadow: `0 6px 0 ${Brand.verdeEscuro}`,
    borderRadius: RaioCard,
    padding: 16,
  },
  bannerAtivoTextos: {
    gap: 3,
  },
  bannerAtivoRotulo: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 12,
    letterSpacing: 1.2,
    color: '#2A5A10',
  },
  bannerAtivoTitulo: {
    fontFamily: Fontes.titulo,
    fontSize: 22,
    color: '#0D2705',
  },
  bannerAtivoProgresso: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 12.5,
    color: '#3F5C1E',
  },
  cardBloqueado: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    backgroundColor: Brand.bgCardEscuro,
    borderWidth: 1,
    borderColor: Brand.bordaForte,
    borderStyle: 'dashed',
    borderRadius: RaioCard,
    padding: 14,
  },
  cardBloqueadoIcone: {
    width: 34,
    height: 34,
    borderRadius: 17,
    backgroundColor: '#1B2029',
    borderWidth: 1,
    borderColor: Brand.borda,
    justifyContent: 'center',
    alignItems: 'center',
  },
  cardBloqueadoTextos: {
    flex: 1,
    gap: 2,
  },
  cardBloqueadoTitulo: {
    fontFamily: Fontes.titulo,
    fontSize: 14,
    color: Brand.textoApagado,
  },
  cardBloqueadoSubtitulo: {
    fontFamily: Fontes.corpo,
    fontSize: 11.5,
    color: Brand.textoMuted,
  },
});
