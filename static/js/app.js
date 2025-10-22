// static/js/app.js - Funções globais COMPLETAS

console.log('✅ app.js carregado!');

// ===== FUNÇÕES GLOBAIS =====

// Função para mostrar notificações
function mostrarNotificacao(mensagem, tipo = 'success') {
    // Criar elemento de alerta
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${tipo} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';

    // Ícones para cada tipo
    const icones = {
        'success': '✅',
        'danger': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    };

    alertDiv.innerHTML = `
        ${icones[tipo] || ''} ${mensagem}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alertDiv);

    // Auto-remover após 5 segundos
    setTimeout(() => {
        if (alertDiv.parentElement) {
            alertDiv.remove();
        }
    }, 5000);
}

// Função para validar dados da transação
function validarTransacao(dados) {
    if (!dados.tipo) {
        throw new Error('Selecione o tipo da transação');
    }
    if (!dados.categoria) {
        throw new Error('Selecione uma categoria');
    }
    if (!dados.valor || dados.valor <= 0) {
        throw new Error('O valor deve ser maior que zero');
    }
    return true;
}

// Função para formatar data
function formatarData(dataString) {
    try {
        const data = new Date(dataString);
        return data.toLocaleString('pt-BR');
    } catch (error) {
        return dataString;
    }
}

// ===== FUNÇÕES PARA TRANSAÇÕES =====

let todasTransacoes = [];

// Carregar transações para a página de transações
async function carregarTransacoesPagina() {
    try {
        console.log('📡 Carregando transações...');
        const response = await fetch('/api/transactions');

        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }

        todasTransacoes = await response.json();
        console.log('✅ Transações carregadas:', todasTransacoes);
        atualizarTabelaTransacoes();

    } catch (error) {
        console.error('❌ Erro ao carregar transações:', error);
        mostrarNotificacao('Erro ao carregar transações: ' + error.message, 'danger');
    }
}

// Atualizar tabela de transações
function atualizarTabelaTransacoes() {
    const tbody = document.getElementById('transactions-table');
    if (!tbody) return;

    if (todasTransacoes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Nenhuma transação cadastrada</td></tr>';
        return;
    }

    const html = todasTransacoes.map(transacao => `
        <tr>
            <td>${transacao.id}</td>
            <td>${formatarData(transacao.data)}</td>
            <td>
                <span class="badge ${transacao.tipo === 'Receita' ? 'bg-success' : 'bg-danger'}">
                    ${transacao.tipo}
                </span>
            </td>
            <td>${transacao.categoria}</td>
            <td class="${transacao.tipo === 'Receita' ? 'text-success' : 'text-danger'}">
                R$ ${transacao.valor.toFixed(2)}
            </td>
            <td>${transacao.descricao || '-'}</td>
            <td>
                <button class="btn btn-sm btn-warning me-1" onclick="editarTransacao(${transacao.id})">
                    ✏️ Editar
                </button>
                <button class="btn btn-sm btn-danger" onclick="excluirTransacao(${transacao.id})">
                    🗑️ Excluir
                </button>
            </td>
        </tr>
    `).join('');

    tbody.innerHTML = html;
}

// Editar transação
function editarTransacao(id) {
    const transacao = todasTransacoes.find(t => t.id === id);
    if (!transacao) {
        mostrarNotificacao('Transação não encontrada', 'danger');
        return;
    }

    document.getElementById('edit-id').value = transacao.id;
    document.getElementById('edit-type').value = transacao.tipo;
    document.getElementById('edit-category').value = transacao.categoria;
    document.getElementById('edit-amount').value = transacao.valor;
    document.getElementById('edit-description').value = transacao.descricao || '';

    // Abrir modal
    const modal = new bootstrap.Modal(document.getElementById('editModal'));
    modal.show();
}

// Salvar edição
async function saveEdit() {
    const id = document.getElementById('edit-id').value;
    const transacao = {
        tipo: document.getElementById('edit-type').value,
        categoria: document.getElementById('edit-category').value,
        valor: parseFloat(document.getElementById('edit-amount').value),
        descricao: document.getElementById('edit-description').value
    };

    try {
        console.log('📤 Salvando edição:', transacao);
        validarTransacao(transacao);

        const response = await fetch(`/api/transactions/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(transacao)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Erro do servidor: ${errorText}`);
        }

        const result = await response.json();
        console.log('✅ Transação atualizada:', result);

        // Fechar modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('editModal'));
        modal.hide();

        await carregarTransacoesPagina();
        mostrarNotificacao('Transação atualizada com sucesso!');

    } catch (error) {
        console.error('❌ Erro ao atualizar transação:', error);
        mostrarNotificacao('Erro: ' + error.message, 'danger');
    }
}

// Excluir transação
async function excluirTransacao(id) {
    if (!confirm('Tem certeza que deseja excluir esta transação?')) {
        return;
    }

    try {
        console.log('🗑️ Excluindo transação:', id);
        const response = await fetch(`/api/transactions/${id}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Erro do servidor: ${errorText}`);
        }

        const result = await response.json();
        console.log('✅ Transação excluída:', result);

        await carregarTransacoesPagina();
        mostrarNotificacao('Transação excluída com sucesso!');

    } catch (error) {
        console.error('❌ Erro ao excluir transação:', error);
        mostrarNotificacao('Erro: ' + error.message, 'danger');
    }
}

// Exportar dados
async function exportData(format) {
    try {
        console.log(`📤 Exportando dados como ${format}...`);
        const response = await fetch(`/api/export/${format}`);

        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }

        if (format === 'json') {
            const data = await response.json();
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'transacoes.json';
            a.click();
            window.URL.revokeObjectURL(url);
        } else if (format === 'csv') {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'transacoes.csv';
            a.click();
            window.URL.revokeObjectURL(url);
        }

        mostrarNotificacao(`Dados exportados como ${format.toUpperCase()}!`);

    } catch (error) {
        console.error('❌ Erro ao exportar:', error);
        mostrarNotificacao('Erro ao exportar dados: ' + error.message, 'danger');
    }
}

// ===== INICIALIZAÇÃO =====

// Disponibilizar funções globalmente
window.mostrarNotificacao = mostrarNotificacao;
window.validarTransacao = validarTransacao;
window.carregarTransacoesPagina = carregarTransacoesPagina;
window.editarTransacao = editarTransacao;
window.excluirTransacao = excluirTransacao;
window.saveEdit = saveEdit;
window.exportData = exportData;