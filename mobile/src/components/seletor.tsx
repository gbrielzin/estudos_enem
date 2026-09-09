import { Feather } from '@expo/vector-icons';
import { useEffect, useState } from 'react';
import { FlatList, Modal, Pressable, StyleSheet, Text, View } from 'react-native';

import { Brand, Fontes, RaioCard } from '@/constants/brand';

interface Opcao {
  valor: string;
  texto: string;
}

interface SeletorProps {
  rotulo: string;
  valor: string | null;
  opcoes: Opcao[];
  aoSelecionar: (valor: string) => void;
  placeholder?: string;
  icone: keyof typeof Feather.glyphMap;
  corIcone: string;
  fundoIcone: string;
  /** Incremente esse número (de fora) pra forçar a abertura do modal
   * -- usado pelo banner clicável da trilha (ver index.tsx, seção 8.2
   * do pedido do usuário) pra reabrir o seletor de matéria sem
   * duplicar a lógica de modal aqui dentro. */
  abrirSinal?: number;
}

/**
 * Picker via Modal + FlatList (evita depender de um módulo nativo de
 * picker só pra seleção única) -- restilizado pra bater com a linha
 * "select" do mockup de referência: badge de ícone colorido + rótulo
 * pequeno em cima do valor + chevron.
 */
export function Seletor({ rotulo, valor, opcoes, aoSelecionar, placeholder = 'Selecione', icone, corIcone, fundoIcone, abrirSinal }: SeletorProps) {
  const [aberto, setAberto] = useState(false);
  const textoSelecionado = opcoes.find((o) => o.valor === valor)?.texto ?? placeholder;

  useEffect(() => {
    if (abrirSinal !== undefined && abrirSinal > 0) setAberto(true);
  }, [abrirSinal]);

  return (
    <>
      <Pressable style={styles.campo} onPress={() => setAberto(true)}>
        <View style={[styles.iconeBadge, { backgroundColor: fundoIcone }]}>
          <Feather name={icone} size={15} color={corIcone} />
        </View>
        <View style={styles.corpo}>
          <Text style={styles.rotulo}>{rotulo}</Text>
          <Text style={styles.valor}>{textoSelecionado}</Text>
        </View>
        <Feather name="chevron-down" size={16} color={Brand.textoMuted} />
      </Pressable>
      <Modal visible={aberto} animationType="slide" transparent onRequestClose={() => setAberto(false)}>
        <Pressable style={styles.fundo} onPress={() => setAberto(false)}>
          <View style={styles.folha}>
            <FlatList
              data={opcoes}
              keyExtractor={(item) => item.valor}
              renderItem={({ item }) => (
                <Pressable
                  style={styles.opcao}
                  onPress={() => {
                    aoSelecionar(item.valor);
                    setAberto(false);
                  }}>
                  <Text style={[styles.opcaoTexto, item.valor === valor && styles.opcaoSelecionadaTexto]}>{item.texto}</Text>
                </Pressable>
              )}
            />
          </View>
        </Pressable>
      </Modal>
    </>
  );
}

const styles = StyleSheet.create({
  campo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderRadius: 16,
    padding: 14,
    marginBottom: 10,
  },
  iconeBadge: {
    width: 30,
    height: 30,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  corpo: {
    flex: 1,
  },
  rotulo: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 11.5,
    color: Brand.textoApagado,
    marginBottom: 2,
  },
  valor: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 14.5,
    color: Brand.texto,
  },
  fundo: {
    flex: 1,
    justifyContent: 'flex-end',
    backgroundColor: '#00000088',
  },
  folha: {
    maxHeight: '70%',
    backgroundColor: Brand.bgCard,
    borderTopLeftRadius: RaioCard,
    borderTopRightRadius: RaioCard,
    paddingVertical: 10,
    borderWidth: 1,
    borderColor: Brand.borda,
  },
  opcao: {
    paddingVertical: 14,
    paddingHorizontal: 20,
  },
  opcaoTexto: {
    fontFamily: Fontes.corpo,
    fontSize: 15,
    color: Brand.texto,
  },
  opcaoSelecionadaTexto: {
    fontFamily: Fontes.corpoExtraNegrito,
    color: Brand.verde,
  },
});
