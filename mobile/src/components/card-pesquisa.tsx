import { useEffect, useState } from 'react';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import { Brand, Fontes, RaioCard } from '@/constants/brand';
import { enviarPesquisa, getUltimaPesquisa } from '@/lib/api';

const DIAS_ENTRE_PERGUNTAS = 7;
const NOTAS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

/** Já passou uma semana desde a última resposta? `criadoEm` vem como 'AAAA-MM-DD HH:MM:SS'. */
export function devePerguntar(criadoEm: string | null, agora: Date = new Date()): boolean {
  if (!criadoEm) return true;
  const ultima = new Date(criadoEm.replace(' ', 'T'));
  if (Number.isNaN(ultima.getTime())) return true;
  return agora.getTime() - ultima.getTime() >= DIAS_ENTRE_PERGUNTAS * 24 * 60 * 60 * 1000;
}

/**
 * Pesquisa curta (NPS) no Perfil: "de 0 a 10, indicaria?" + o que mais
 * ajudou. Aparece no máximo uma vez por semana (GET /pesquisa/ultima) e
 * some sozinha se a API falhar: pesquisa nunca atrapalha o estudo.
 */
export function CardPesquisa() {
  const [mostrar, setMostrar] = useState(false);
  const [nota, setNota] = useState<number | null>(null);
  const [comentario, setComentario] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [enviado, setEnviado] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    getUltimaPesquisa()
      .then((criadoEm) => setMostrar(devePerguntar(criadoEm)))
      .catch(() => setMostrar(false));
  }, []);

  if (!mostrar) return null;

  if (enviado) {
    return (
      <View style={styles.card}>
        <Text style={styles.titulo}>Valeu! Isso me ajuda a melhorar o app. 💜</Text>
      </View>
    );
  }

  function enviar() {
    if (nota === null) return;
    setEnviando(true);
    setErro(null);
    enviarPesquisa(nota, comentario)
      .then(() => setEnviado(true))
      .catch((e) => setErro(e instanceof Error ? e.message : String(e)))
      .finally(() => setEnviando(false));
  }

  return (
    <View style={styles.card}>
      <Text style={styles.titulo}>De 0 a 10, quanto você indicaria o app para um amigo?</Text>
      <View style={styles.notas}>
        {NOTAS.map((n) => (
          <Pressable
            key={n}
            onPress={() => setNota(n)}
            style={[styles.nota, nota === n && styles.notaEscolhida]}
            accessibilityRole="button"
            accessibilityLabel={`Nota ${n}`}>
            <Text style={[styles.notaTexto, nota === n && styles.notaTextoEscolhida]}>{n}</Text>
          </Pressable>
        ))}
      </View>
      <TextInput
        style={styles.campo}
        placeholder="O que mais te ajudou? (opcional)"
        placeholderTextColor={Brand.textoApagado}
        value={comentario}
        onChangeText={setComentario}
        maxLength={500}
        multiline
      />
      {erro && <Text style={styles.erro}>⚠️ {erro}</Text>}
      <Pressable
        onPress={enviar}
        disabled={nota === null || enviando}
        style={[styles.botao, (nota === null || enviando) && styles.botaoDesligado]}>
        <Text style={styles.botaoTexto}>{enviando ? 'Enviando...' : 'Enviar'}</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderRadius: RaioCard,
    padding: 16,
    gap: 12,
  },
  titulo: { fontFamily: Fontes.corpoExtraNegrito, fontSize: 15, color: Brand.texto },
  notas: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  nota: {
    width: 38,
    height: 38,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: Brand.bordaForte,
    backgroundColor: Brand.bgCardEscuro,
    justifyContent: 'center',
    alignItems: 'center',
  },
  notaEscolhida: { backgroundColor: Brand.roxo, borderColor: Brand.roxo },
  notaTexto: { fontFamily: Fontes.corpoNegrito, fontSize: 14, color: Brand.textoSuave },
  notaTextoEscolhida: { color: Brand.branco },
  campo: {
    minHeight: 64,
    borderWidth: 1,
    borderColor: Brand.bordaForte,
    borderRadius: 12,
    padding: 10,
    fontFamily: Fontes.corpo,
    fontSize: 14,
    color: Brand.texto,
    textAlignVertical: 'top',
  },
  erro: { fontFamily: Fontes.corpo, fontSize: 13, color: Brand.laranja },
  botao: { backgroundColor: Brand.verde, borderRadius: 14, paddingVertical: 12, alignItems: 'center' },
  botaoDesligado: { opacity: 0.4 },
  botaoTexto: { fontFamily: Fontes.corpoExtraNegrito, fontSize: 15, color: Brand.bg },
});
