from setuptools import setup, find_packages

def parse_requirements(fname='requirements.txt'):
    """Retorna uma lista de dependências, ignorando comentários e linhas vazias."""
    with open(fname, 'r', encoding='utf-8') as f:
        lines = [
            line.strip() for line in f
            if line.strip() and not line.strip().startswith('#')
        ]
    return lines

setup(
    name="fiap_vitivinicultura",
    version="0.1.0",
    author="Seu Nome",
    author_email="seu@email.com",
    description="API para dados de vitivinicultura da Embrapa",
    python_requires=">=3.9.7,<3.10",
    packages=find_packages(),
    install_requires=parse_requirements(),  # lê direto do requirements.txt
)