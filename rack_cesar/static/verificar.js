document.addEventListener("DOMContentLoaded", function() {
    document.querySelector(".responder").addEventListener("click", function() {
        const questaoId = document.getElementById("questao_id").value;
        const respostaSelecionada = document.querySelector('input[name="answer"]:checked');

        if (!respostaSelecionada) {
            alert("❌ Selecione uma alternativa antes de enviar!");
            return;
        }

        fetch("/verificar_resposta", {
            method: "POST",
            body: new URLSearchParams({
                questao_id: questaoId,
                answer: respostaSelecionada.value
            }),
            headers: { "Content-Type": "application/x-www-form-urlencoded" }
        })
        .then(response => response.json())
        .then(data => {
            const resultadoDiv = document.getElementById("resultado");

            if (resultadoDiv) {
                resultadoDiv.textContent = data.resultado;
                resultadoDiv.style.color = data.resultado.includes("correta") ? "green" : "red";
            }

            document.getElementById("acertos").textContent = `✅ Acertos: ${data.acertos}`;
            document.getElementById("erros").textContent = `❌ Erros: ${data.erros}`;
        })
        .catch(error => console.error("Erro na requisição:", error));
    });
});


function reiniciarHistorico(materia) {
    fetch("/reiniciar_historico", {
        method: "POST",
        body: new URLSearchParams({ materia: materia }),
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
    })
    .then(response => response.json())
    .then(data => {
        alert(data.mensagem);
        document.getElementById("acertos").textContent = `✅ Acertos: ${data.acertos}`;
        document.getElementById("erros").textContent = `❌ Erros: ${data.erros}`;
        
        // Atualiza para a primeira questão
        mudarQuestao(materia, "reiniciar");
    })
    .catch(error => console.error("Erro ao reiniciar histórico:", error));
}


function verificarResposta(materia) {
    const questaoId = document.getElementById("questao_id").value;
    const respostaSelecionada = document.querySelector('input[name="answer"]:checked');

    if (!respostaSelecionada) {
        alert("❌ Selecione uma alternativa antes de enviar!");
        return;
    }

    fetch("/verificar_resposta", {
        method: "POST",
        body: new URLSearchParams({
            materia: materia, 
            answer: respostaSelecionada.value
        }),
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("resultado").textContent = data.resultado;
        document.getElementById("acertos").textContent = `✅ Acertos: ${data.acertos}`;
        document.getElementById("erros").textContent = `❌ Erros: ${data.erros}`;
        
        // Após 2 segundos, passa para a próxima questão
        setTimeout(() => {
            mudarQuestao(materia, 'proxima');
        }, 2000);
    })
    .catch(error => console.error("Erro na requisição:", error));
}


function mudarQuestao(materia, direcao) {
    fetch("/mudar_questao", {
        method: "POST",
        body: new URLSearchParams({ materia: materia, direcao: direcao }),
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
    })
    .then(response => response.json())
    .then(data => {
        document.querySelector(".pergunta").textContent = data.texto;
        
        // Atualiza as alternativas dinamicamente
        const alternativas = ["a", "b", "c", "d", "e"];
        document.querySelectorAll(".options label").forEach((label, index) => {
            label.innerHTML = `<input type="radio" name="answer" value="${String.fromCharCode(65 + index)}"> ${String.fromCharCode(65 + index)}) ${data[`alternativa_${alternativas[index]}`]}`;
        });

        document.getElementById("questao_id").value = data.id;
        document.getElementById("resultado").textContent = "";
    })
    .catch(error => console.error("Erro ao mudar questão:", error));
}