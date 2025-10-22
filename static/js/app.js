// static/js/app.js
console.log("✅ app.js carregado!");

// ---------- Utilidades ----------
function qsAny(selectors, root = document) {
  for (const sel of selectors) {
    const el = root.querySelector(sel);
    if (el) return el;
  }
  return null;
}

function logWarnMissing(name, selectors) {
  console.warn(`⚠️ Elemento "${name}" não encontrado. Procure por um destes seletores no HTML: ${selectors.join(", ")}`);
}

function mostrarNotificacao(mensagem, tipo = "success") {
  const alerta = document.createElement("div");
  alerta.className = `alert alert-${tipo === "success" ? "success" : "danger"} alert-dismissible fade show`;
  alerta.role = "alert";
  alerta.innerHTML = `
    ${mensagem}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  (document.querySelector(".container") || document.body).prepend(alerta);
  setTimeout(() => alerta.remove(), 3000);
}

// ---------- Estado ----------
const CATEGORIAS = {
  Receita: [
    { nome: "Salário", icone: "💼" },
    { nome: "Freelance", icone: "🧑‍💻" },
    { nome: "Investimentos", icone: "📈" },
    { nome: "Outros Ganhos", icone: "💰" },
  ],
  Despesa: [
    { nome: "Alimentação", icone: "🍔" },
    { nome: "Moradia", icone: "🏠" },
    { nome: "Transporte", icone: "🚗" },
    { nome: "Lazer", icone: "🎮" },
    { nome: "Saúde", icone: "💊" },
    { nome: "Outros Gastos", icone: "💸" },
  ],
};

// ---------- DOM refs (com fallback de seletores) ----------
function getRefs() {
  const form = qsAny(["#form-transacao", "form#formTransacao", "form[data-form='transacao']"]);
  const tipo = qsAny(["#tipo", "#select-tipo", "[name='tipo']"]);
  const categoria = qsAny(["#categoria", "#select-categoria", "[name='categoria']"]);
  const valor = qsAny(["#valor", "input[name='valor']"]);
  const descricao = qsAny(["#descricao", "input[name='descricao']"]);
  const tabela = qsAny(["#tabela-transacoes", "#tabelaTransacoes", "table[data-table='transacoes']"]);
  const tbody = tabela ? tabela.querySelector("tbody") : null;

  return { form, tipo, categoria, valor, descricao, tabela, tbody };
}

// ---------- Categorias (popular/filtro) ----------
function popularCategoriasPorTipo(selectTipo, selectCategoria) {
  if (!selectTipo || !selectCategoria) return;

  const tipoVal = selectTipo.value;
  const lista = CATEGORIAS[tipoVal] || [];
  selectCategoria.innerHTML = '<option selected>Selecione...</option>';

  lista.forEach((cat) => {
    const opt = document.createElement("option");
    opt.value = cat.nome;
    opt.textContent = `${cat.icone} ${cat.nome}`;
    selectCategoria.appendChild(opt);
  });

  console.log(`🔎 Tipo selecionado: ${tipoVal} → categorias:`, lista.map((c) => c.nome));
}

function configurarFiltroCategorias(refs) {
  const { tipo, categoria } = refs;

  if (!tipo) logWarnMissing("tipo", ["#tipo", "#select-tipo", "[name='tipo']"]);
  if (!categoria) logWarnMissing("categoria", ["#categoria", "#select-categoria", "[name='categoria']"]);
  if (!tipo || !categoria) return;

  // Popular na carga inicial (caso já venha "Receita" ou "Despesa" selecionado)
  popularCategoriasPorTipo(tipo, categoria);

  // E reagir às mudanças
  tipo.addEventListener("change", () => popularCategoriasPorTipo(tipo, categoria));
}

// ---------- Transações (LocalStorage) ----------
function lerTransacoes() {
  try {
    return JSON.parse(localStorage.getItem("transacoes")) || [];
  } catch {
    return [];
  }
}

function salvarTransacoes(arr) {
  localStorage.setItem("transacoes", JSON.stringify(arr));
}

function renderizarTransacoes(refs) {
  const { tabela, tbody } = refs;
  console.log("Carregando transações...");

  if (!tabela) {
    logWarnMissing("tabela de transações", ["#tabela-transacoes", "#tabelaTransacoes", "table[data-table='transacoes']"]);
    return;
  }
  if (!tbody) {
    console.warn("⚠️ A tabela de transações existe, mas não há <tbody> dentro dela.");
    return;
  }

  tbody.innerHTML = "";
  const transacoes = lerTransacoes();
  console.log("📊 Transações carregadas:", transacoes);

  if (transacoes.length === 0) {
    const linha = document.createElement("tr");
    linha.innerHTML = `<td colspan="7" class="text-center text-muted">Nenhuma transação cadastrada</td>`;
    tbody.appendChild(linha);
    return;
  }

  transacoes.forEach((t, i) => {
    const linha = document.createElement("tr");
    linha.innerHTML = `
      <td>${i + 1}</td>
      <td>${t.data}</td>
      <td>${t.tipo}</td>
      <td>${t.categoria}</td>
      <td>R$ ${Number(t.valor).toFixed(2)}</td>
      <td>${t.descricao}</td>
      <td><button class="btn btn-danger btn-sm" data-index="${i}">Excluir</button></td>
    `;
    tbody.appendChild(linha);
  });

  // Delegação para excluir
  tbody.querySelectorAll("button.btn-danger").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const idx = Number(e.currentTarget.getAttribute("data-index"));
      excluirTransacao(idx, refs);
    });
  });
}

function adicionarTransacao(refs) {
  const { tipo, categoria, valor, descricao, form } = refs;

  if (!tipo || !categoria || !valor || !descricao) {
    mostrarNotificacao("Campos do formulário não encontrados. Verifique os IDs/nomes.", "error");
    return;
  }

  const tipoVal = (tipo.value || "").trim();
  const catVal = (categoria.value || "").trim();
  const valorNum = parseFloat(valor.value);
  const descVal = (descricao.value || "").trim();

  if (!tipoVal || tipoVal === "Selecione...") {
    mostrarNotificacao("Selecione o tipo da transação!", "error");
    return;
  }
  if (!catVal || catVal === "Selecione...") {
    mostrarNotificacao("Selecione a categoria!", "error");
    return;
  }
  if (isNaN(valorNum) || valorNum <= 0) {
    mostrarNotificacao("Informe um valor válido!", "error");
    return;
  }
  if (!descVal) {
    mostrarNotificacao("Informe uma descrição!", "error");
    return;
  }

  const nova = {
    tipo: tipoVal,
    categoria: catVal,
    valor: valorNum,
    descricao: descVal,
    data: new Date().toLocaleString(),
  };

  const transacoes = lerTransacoes();
  transacoes.push(nova);
  salvarTransacoes(transacoes);

  mostrarNotificacao("Transação adicionada com sucesso!");
  if (form) form.reset();

  // Após reset, re-popular categorias conforme tipo atual (se o select tipo tiver um valor default)
  popularCategoriasPorTipo(tipo, categoria);

  renderizarTransacoes(refs);
}

function excluirTransacao(index, refs) {
  const transacoes = lerTransacoes();
  transacoes.splice(index, 1);
  salvarTransacoes(transacoes);
  mostrarNotificacao("Transação excluída!");
  renderizarTransacoes(refs);
}

// ---------- Inicialização ----------
document.addEventListener("DOMContentLoaded", () => {
  console.log("🚀 DOM carregado.");
  const refs = getRefs();

  // Configurar filtro de categorias
  configurarFiltroCategorias(refs);

  // Bind do formulário
  if (!refs.form) {
    logWarnMissing("formulário de transação", ["#form-transacao", "form#formTransacao", "form[data-form='transacao']"]);
  } else {
    refs.form.addEventListener("submit", (e) => {
      e.preventDefault();
      adicionarTransacao(refs);
    });
  }

  // Renderizar transações salvas
  renderizarTransacoes(refs);

  // Dica de IDs encontrados (para diagnosticar rapidamente)
  console.table({
    form: !!refs.form,
    tipo: !!refs.tipo,
    categoria: !!refs.categoria,
    valor: !!refs.valor,
    descricao: !!refs.descricao,
    tabela: !!refs.tabela,
  });
});
