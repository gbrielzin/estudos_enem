import { useEffect, useState } from 'react';
import { Image, StyleSheet } from 'react-native';

import { urlImagemEnunciado } from '@/lib/api';

/**
 * Figura/gráfico/tabela da questão (`enunciado_imagem_path`, ~400 questões
 * oficiais). Ocupa a largura do card e mantém a proporção real da imagem,
 * que só é conhecida depois de carregar (Image.getSize). Sem caminho, ou
 * se a imagem falhar, não ocupa espaço nenhum.
 */
export function FiguraEnunciado({ caminho }: { caminho: string | null }) {
  const url = urlImagemEnunciado(caminho);
  const [proporcao, setProporcao] = useState<number | null>(null);
  const [falhou, setFalhou] = useState(false);

  useEffect(() => {
    setProporcao(null);
    setFalhou(false);
    if (!url) {
      return;
    }
    Image.getSize(
      url,
      (largura, altura) => setProporcao(altura > 0 ? largura / altura : null),
      () => setFalhou(true),
    );
  }, [url]);

  if (!url || falhou || proporcao === null) {
    return null;
  }
  return (
    <Image
      source={{ uri: url }}
      style={[styles.figura, { aspectRatio: proporcao }]}
      resizeMode="contain"
      accessibilityLabel="Figura da questão"
    />
  );
}

const styles = StyleSheet.create({
  figura: {
    width: '100%',
    marginTop: 12,
    borderRadius: 8,
    backgroundColor: '#FFFFFF',
  },
});
