// Arquivo: static/parceiros.js

// FUNÇÃO PARA PEGAR O PARÂMETRO DA URL
function getProjectIdFromUrl() {
    // Esta função está ajustada para ser usada quando o link for um projeto específico (ex: ?id=projeto1)
    // Como o botão principal na portfolio.html não envia ID, a página exibirá o 'projeto1' por padrão.
    const params = new URLSearchParams(window.location.search);
    return params.get('id') || 'projeto1'; // Default para projeto1
}

// DADOS DE PROJETOS (ATUALIZADOS COM PROFESSORES E PARTICIPANTES DETALHADOS)
const projectData = {
    'projeto1': {
        title: 'PROJETO DE DESTAQUE: CRIAÇÃO DO CREATHUB',
        
        // Dados dos professores
        professors: [
            { 
                name: 'Ramon', 
                role: 'Marketing Digital', 
                social: 'https://www.instagram.com/ramon.digital/',
                description: 'Responsável pela estratégia e criação de conteúdo digital, focando na visibilidade e engajamento da plataforma. Marketing Digital envolve SEO, mídias sociais e campanhas pagas.'
            }, 
            { 
                name: 'Nathália', 
                role: 'Desenvolvimento do site: Front e Back End', 
                social: 'https://www.instagram.com/nath_dev_/',
                description: 'Supervisão técnica e arquitetura de código, garantindo a funcionalidade e a escalabilidade do sistema em todas as camadas (servidor e interface).' 
            },
            { 
                name: 'Kennedy', 
                role: 'Design', 
                social: 'https://www.instagram.com/ateliekosmico/',
                description: 'Orientação na concepção visual, identidade de marca e experiência do usuário (UX/UI) do portal, assegurando a estética e usabilidade.'
            }
        ],
        
        // Dados dos participantes (alunos)
        participants: [
            { 
                name: 'Gustavo', 
                role: 'Desenvolvimento do site / Back End', 
                social: 'https://www.instagram.com/guh_ettinger/',
                description: 'Implementação da lógica de servidor e gerenciamento do banco de dados para todas as funcionalidades dinâmicas do site.' 
            },
            { 
                name: 'Rogério', 
                role: 'Marketing', 
                social: 'https://www.instagram.com/rogerio_mazini/',
                description: 'Suporte na execução das estratégias de marketing digital e análise de métricas de desempenho.'
            },
            { 
                name: 'HJR Informática', 
                role: 'Parte Visual do Site (Front End)', 
                social: 'https://www.instagram.com/hjr_informatica/',
                description: 'Responsável pela tradução do design em código, focando na interatividade e responsividade da interface do usuário.'
            }
        ]
    },
    // Adicione outros projetos aqui se necessário
};

// FUNÇÃO PRINCIPAL PARA EXIBIR DETALHES
document.addEventListener('DOMContentLoaded', () => {
    const projectId = getProjectIdFromUrl();
    const detailsDiv = document.getElementById('partners-details');
    const data = projectData[projectId];

    if (!data) {
        detailsDiv.innerHTML = '<h2>Projeto Não Encontrado</h2><p>Verifique o link ou a base de dados do projeto.</p>';
        return;
    }

    let htmlContent = `<h2><i class="fa-solid fa-folder-open"></i> ${data.title}</h2>`;
    
    // --- 1. CONSTRUÇÃO DOS PROFESSORES ---
    htmlContent += '<h3><i class="fa-solid fa-graduation-cap"></i> Professores Responsáveis</h3><ul>';
    data.professors.forEach(p => {
        const socialLink = p.social ? 
            `<a href="${p.social}" target="_blank" class="social-link" title="Instagram de ${p.name}">
                <i class="fab fa-instagram"></i>
            </a>` : '';
        
        htmlContent += `
            <li>
                <strong>${p.name}</strong> (${p.role})${socialLink}
                <p>${p.description}</p>
            </li>`;
    });
    htmlContent += '</ul>';

    // --- 2. CONSTRUÇÃO DOS PARTICIPANTES (ALUNOS) ---
    htmlContent += '<h3><i class="fa-solid fa-user-group"></i> Participantes do Projeto</h3><ul>';
    data.participants.forEach(p => {
        const socialLink = p.social ? 
            `<a href="${p.social}" target="_blank" class="social-link" title="Instagram de ${p.name}">
                <i class="fab fa-instagram"></i>
            </a>` : '';
        
        htmlContent += `
            <li>
                <strong>${p.name}</strong> (${p.role})${socialLink}
                <p>${p.description}</p>
            </li>`;
    });
    htmlContent += '</ul>';

    detailsDiv.innerHTML = htmlContent;
});