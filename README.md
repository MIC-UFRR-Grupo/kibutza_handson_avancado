# Protótipo: Sistema de Monitoramento de Cadeia de Frio

## Banco de Dados
- **Tecnologia**: Firebase Realtime Database (nuvem, plano gratuito).
- **Estrutura**: Dados de sensores (temperatura, umidade, UV) e alertas.
- **Acesso**: Via Python (`firebase-admin`) e dashboard Streamlit.
- **Funcionalidades**:
  - Gráficos em tempo real (dashboard).
  - Alertas para condições críticas.
  - Histórico para auditoria (simulado).

## Como Demonstrar
1. Execute `python insert_data.py` para inserir dados simulados.
2. Execute `streamlit run dashboard.py` para visualizar o dashboard.
3. Acesse o Firebase Console para ver os dados brutos.

## Próximos Passos
- Integrar MQTT para coleta de dados reais.
- Implementar alertas remotos (e-mail/SMS).