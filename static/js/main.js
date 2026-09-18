// // click to add new item
// $(document).on("click", "#add-item", function () {
//     var numberOfItems = $("#wrapper").children().length + 1;

//     let formAdd = `
//         <div class="form-row">
//             <div class="form-group col-md-4">
//                 <label for="article-${numberOfItems}">#${numberOfItems} Item Name</label>
//                 <input type="text" required class="form-control" id="article-${numberOfItems}" name="article">
//             </div>
//             <div class="form-group col-md-2">
//                 <label for="qty-${numberOfItems}">Quantity</label>
//                 <input type="number" min="1" step="0.1" required class="form-control" id="qty-${numberOfItems}" name="qty">
//             </div>
//             <div class="form-group col-md-3">
//                 <label for="unit_price-${numberOfItems}">Unit Price</label>
//                 <input type="number" min="0" step="0.01" onchange="handleChangeSingleArticle(this.id)" required class="form-control" id="unit_price-${numberOfItems}"
//                     name="unit_price">
//             </div>
//             <div class="form-group col-md-3">
//                 <label for="total_price-a-${numberOfItems}">Total</label>
//                 <input type="number" min="0" step="0.01" readonly class="form-control" id="total_price-a-${numberOfItems}"
//                     name="total_price-a">
//             </div>
//         </div>
//     `
//     $("#wrapper:last").append(formAdd);
// })

// // click to remove the last item
// $(document).on("click", "#remove-item", function () {
//     $("#wrapper:last").children().last().remove();
// });

// // calculate total price for each item

// function handleChangeSingleArticle(id) {
//     let articleId = id.toString().split("-")[1];
//     let idQty = `#qty-${articleId}`;
//     let idUnitPrice = `#unit_price-${articleId}`;
//     let totalIdLine = `#total_price-a-${articleId}`;
//     let totalLine = parseFloat($(idQty).val()) * parseFloat($(idUnitPrice).val());

//     $(totalIdLine).val(totalLine);

//     $('#total_price').val(parseFloat($('#total_price').val()) + totalLine);
// }


// Variable globale pour garantir des ID uniques même après suppression
var itemCounter = $("#wrapper").children().length;

// click to add new item
$(document).on("click", "#add-item", function () {
    itemCounter++; // On incrémente le compteur unique

    let formAdd = `
        <div class="form-row">
            <div class="form-group col-md-4">
                <label for="article-${itemCounter}">#${itemCounter} Item Name</label>
                <input type="text" required class="form-control" id="article-${itemCounter}" name="article">
            </div>
            <div class="form-group col-md-2">
                <label for="qty-${itemCounter}">Quantity</label>
                <input type="number" min="1" step="0.1" required class="form-control" id="qty-${itemCounter}" name="qty">
            </div>
            <div class="form-group col-md-3">
                <label for="unit_price-${itemCounter}">Unit Price</label>
                <input type="number" min="0" step="0.01" onchange="handleChangeSingleArticle(this.id)" required class="form-control" id="unit_price-${itemCounter}" name="unit_price">
            </div>
            <div class="form-group col-md-3">
                <label for="total_price-a-${itemCounter}">Total</label>
                <input type="number" min="0" step="0.01" readonly class="form-control" id="total_price-a-${itemCounter}" name="total_price-a">
            </div>
        </div>
    `;
    $("#wrapper").append(formAdd);
});

// click to remove the last item
$(document).on("click", "#remove-item", function () {
    // On ne supprime que s'il reste plus d'une ligne (optionnel mais recommandé)
    if ($("#wrapper").children().length > 1) {
        $("#wrapper").children().last().remove();
        calculateGrandTotal(); // Recalculer le total général après suppression
    }
});

// calculate total price for each item
function handleChangeSingleArticle(id) {
    let articleId = id.toString().split("-")[1];
    let idQty = `#qty-${articleId}`;
    let idUnitPrice = `#unit_price-${articleId}`;
    let totalIdLine = `#total_price-a-${articleId}`;
    
    // Sécurité : Remplacer par 0 si le champ est vide pour éviter le bug du NaN
    let qty = parseFloat($(idQty).val()) || 0;
    let unitPrice = parseFloat($(idUnitPrice).val()) || 0;
    
    // Calcul et affichage du prix de la ligne (arrondi à 2 décimales)
    let totalLine = qty * unitPrice;
    $(totalIdLine).val(totalLine.toFixed(2));

    // Recalcul global de la facture
    calculateGrandTotal();
}

// Nouvelle fonction pour calculer proprement le total général
function calculateGrandTotal() {
    let grandTotal = 0;
    
    // On parcourt chaque input de total de ligne
    $('input[name="total_price-a"]').each(function() {
        let value = parseFloat($(this).val()) || 0;
        grandTotal += value;
    });
    
    // Mise à jour du champ Grand Total
    $('#total_price').val(grandTotal.toFixed(2));
}
