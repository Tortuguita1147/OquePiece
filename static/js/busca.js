/* Busca de personagem com miniatura */
(function () {
    var lista = window.LISTA_PERSONAGENS || [];

    function semAcento(s) {
        return s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
    }

    var indexado = lista.map(function (n) {
        return { nome: n, chave: semAcento(n) };
    });

    function retrato(nome) {
        return "/retrato/" + encodeURIComponent(nome);
    }

    function montar(input) {
        var wrap = document.createElement("div");
        wrap.className = "ac-wrap";
        input.parentNode.insertBefore(wrap, input);
        wrap.appendChild(input);

        var painel = document.createElement("div");
        painel.className = "ac-lista";
        painel.hidden = true;
        wrap.appendChild(painel);

        var ativos = [];
        var selecionado = -1;

        function fechar() {
            painel.hidden = true;
            selecionado = -1;
        }

        function escolher(nome) {
            input.value = nome;
            fechar();
        }

        function desenhar() {
            painel.innerHTML = "";
            ativos.forEach(function (nome, i) {
                var item = document.createElement("div");
                item.className = "ac-item" + (i === selecionado ? " ativo" : "");

                var img = document.createElement("img");
                img.className = "ac-foto";
                img.src = retrato(nome);
                img.alt = "";
                img.loading = "lazy";

                var span = document.createElement("span");
                span.className = "ac-nome";
                span.textContent = nome;

                item.appendChild(img);
                item.appendChild(span);
                item.addEventListener("mousedown", function (e) {
                    e.preventDefault();
                    escolher(nome);
                });
                painel.appendChild(item);
            });
            painel.hidden = ativos.length === 0;
        }

        function filtrar() {
            var q = semAcento(input.value.trim());
            if (!q) {
                ativos = [];
                fechar();
                return;
            }
            var comeca = [], contem = [];
            for (var i = 0; i < indexado.length; i++) {
                var it = indexado[i];
                if (it.chave.indexOf(q) === 0) comeca.push(it.nome);
                else if (it.chave.indexOf(q) !== -1) contem.push(it.nome);
            }
            ativos = comeca.concat(contem).slice(0, 8);
            selecionado = ativos.length ? 0 : -1;
            desenhar();
        }

        input.addEventListener("input", filtrar);
        input.addEventListener("focus", filtrar);
        input.addEventListener("blur", function () { setTimeout(fechar, 120); });
        input.addEventListener("keydown", function (e) {
            if (painel.hidden) return;
            if (e.key === "ArrowDown") {
                e.preventDefault();
                selecionado = Math.min(selecionado + 1, ativos.length - 1);
                desenhar();
            } else if (e.key === "ArrowUp") {
                e.preventDefault();
                selecionado = Math.max(selecionado - 1, 0);
                desenhar();
            } else if (e.key === "Enter" && selecionado >= 0) {
                e.preventDefault();
                escolher(ativos[selecionado]);
            } else if (e.key === "Escape") {
                fechar();
            }
        });
    }

    document.querySelectorAll("input.busca-personagem").forEach(montar);
})();
