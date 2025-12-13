FROM solr:9

ARG CORE=cbo

USER root

# Cria um configset custom dentro da imagem (não é sobrescrito pelo volume /var/solr)
RUN mkdir -p /opt/solr/server/solr/configsets/${CORE}/conf

# ✅ Seus arquivos estão em solr-config/cbo/conf/
# ⚠️ Seu managed schema está como managed-schema.xml,
#    mas o Solr espera o nome "managed-schema"
COPY solr-config/cbo/conf/managed-schema.xml /opt/solr/server/solr/configsets/${CORE}/conf/managed-schema
COPY solr-config/cbo/conf/solrconfig.xml     /opt/solr/server/solr/configsets/${CORE}/conf/solrconfig.xml

# (Opcional) se você usa stopwords/synonyms/protwords/lang, copie também:
COPY solr-config/cbo/conf/ /opt/solr/server/solr/configsets/${CORE}/conf/

RUN chown -R solr:solr /opt/solr/server/solr/configsets/${CORE}

USER solr
