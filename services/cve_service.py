import re
import requests

# Mapeamento de falhas críticas por fabricante e versão de correção
CATALOGO_AUDITORIA = {
    "AMD": {
        "cve_id": "CVE-2023-20593",
        "versao_corrigida": (1, 2, 0, 7),
        "nome_falha": "Zenbleed"
    },
    "INTEL": {
        "cve_id": "CVE-2022-40982",
        "versao_corrigida": (2024, 1, 0, 0),
        "nome_falha": "Downfall"
    }
}


def extrair_versao_numerica(versao_str: str) -> tuple:
    """Converte o texto da versão em tupla numérica para comparação."""
    s = versao_str or ""
    match = re.search(r'(\d+(?:\.\d+)+)', s)
    if match:
        partes = [int(p) for p in match.group(1).split('.')]
    else:
        nums = re.findall(r'\d+', s)
        partes = [int(n) for n in nums] if nums else [0]

    while len(partes) < 4:
        partes.append(0)
    return tuple(partes[:4])


def consultar_vulnerabilidades(fabricante: str, microcodigo: str = "") -> list:
    """Consulta a API do CIRCL e verifica se o microcódigo continua vulnerável."""
    fab_upper = (fabricante or "").strip().upper()
    fab_key = "AMD" if "AMD" in fab_upper else "INTEL"
    regra = CATALOGO_AUDITORIA[fab_key]
    cve_id = regra["cve_id"]

    url_circl = f"https://cve.circl.lu/api/cve/{cve_id}"

    print(f"\n=======================================================", flush=True)
    print(f"[CIRCL API] Fabricante: {fab_key} | Microcódigo: '{microcodigo}'", flush=True)
    print(f"[CIRCL API] Requisição externa: {url_circl}", flush=True)

    # Consulta a API pública do CIRCL
    cve_data = None
    try:
        res = requests.get(url_circl, timeout=5)
        print(f"[CIRCL API] Status HTTP: {res.status_code}", flush=True)

        if res.status_code == 200:
            cve_data = res.json()
            print(f"[CIRCL API] Dados de {cve_id} obtidos com sucesso.", flush=True)
        else:
            print(f"[CIRCL API] Resposta {res.status_code}. Usando fallback local.", flush=True)
    except Exception as e:
        print(f"[CIRCL API] Erro de conexão ({e}). Usando fallback local.", flush=True)

    # Comparação da versão informada com a versão corrigida
    versao_atual = extrair_versao_numerica(microcodigo)
    versao_segura = regra["versao_corrigida"]

    print(f"[CIRCL API] Versão informada: {versao_atual} | Mínima corrigida: {versao_segura}", flush=True)

    # Se a versão for inferior à corrigida, registra a vulnerabilidade
    if versao_atual < versao_segura:
        print(f"[CIRCL API] Microcódigo vulnerável ({cve_id}).", flush=True)

        if cve_data:
            descricao = cve_data.get("summary", f"Vulnerabilidade em microcódigos anteriores a {versao_segura}.")
            cvss = cve_data.get("cvss") or cve_data.get("cvss3") or 7.5
        else:
            descricao = f"Vulnerabilidade crítica {regra['nome_falha']} em processadores {fab_key}."
            cvss = 7.5

        resultado = [{
            "cve_id": cve_id,
            "descricao": str(descricao)[:200],
            "cvss_score": float(cvss)
        }]
    else:
        # Versão segura
        print(f"[CIRCL API] Microcódigo em conformidade. Risco mitigado.", flush=True)
        resultado = []

    print(f"[CIRCL API] Auditoria concluída. Falhas ativas: {len(resultado)}", flush=True)
    print(f"=======================================================\n", flush=True)

    return resultado