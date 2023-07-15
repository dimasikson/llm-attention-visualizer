var MAIN_RESPONSE_JSON = {};

// ------------------------- GENERATE TEXT ON SUBMIT -------------------------

document.getElementById("prompt-form").addEventListener("submit", async function(event) { // note the async here
    event.preventDefault(); // prevent the form from refreshing the page

    // get the prompt text and clear the input
    var prompt_text = document.getElementById("prompt-input");
    MAIN_RESPONSE_JSON["input_text"] = prompt_text.value;

    // hide elements
    document.getElementById("input-text").hidden = true;
    document.getElementById("summary-text").hidden = true;

    // clear the input and summary text
    document.getElementById("prompt-input").value = "";
    document.getElementById("input-text-content").innerHTML = "";
    document.getElementById("summary-text-content").innerHTML = "";

    // encode the prompt text into tokens
    const encode_response = await fetch("/encode", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ "text": MAIN_RESPONSE_JSON["input_text"] })
    });
    
    const encode_response_json = await encode_response.json();
    MAIN_RESPONSE_JSON["input_token_ids"] = encode_response_json["token_ids"];
    MAIN_RESPONSE_JSON["input_token_mapping"] = encode_response_json["token_mapping"];
    MAIN_RESPONSE_JSON["input_sentence_mapping"] = encode_response_json["sentence_mapping"];

    // update input text
    document.getElementById("input-text").hidden = false;
    document.getElementById("input-text-content").innerHTML = highlight_input_text(
        input_text = MAIN_RESPONSE_JSON["input_text"],
        index_mapping = MAIN_RESPONSE_JSON["input_token_mapping"],
        attentions_per_character = empty_array(MAIN_RESPONSE_JSON["input_text"].length)
    )

    // generate the text
    const generate_response = await fetch("/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ "token_ids": MAIN_RESPONSE_JSON["input_token_ids"] })
    });

    const generate_response_json = await generate_response.json();
    MAIN_RESPONSE_JSON["output_token_ids"] = generate_response_json["token_ids"];
    MAIN_RESPONSE_JSON["cross_attentions"] = generate_response_json["cross_attentions"];

    // decode the tokens into text
    const decode_response = await fetch("/decode", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ "token_ids": MAIN_RESPONSE_JSON["output_token_ids"] })
    });

    const decode_response_json = await decode_response.json();
    MAIN_RESPONSE_JSON["output_text"] = decode_response_json["text"];
    MAIN_RESPONSE_JSON["output_token_mapping"] = decode_response_json["token_mapping"];
    MAIN_RESPONSE_JSON["output_sentence_mapping"] = decode_response_json["sentence_mapping"];

    // update summary text
    document.getElementById("summary-text").hidden = false;
    document.getElementById("summary-text-content").innerHTML = MAIN_RESPONSE_JSON["output_text"];
});

// ------------------------- HIGHLIGHT TEXT ON MOUSE UP -------------------------

document.addEventListener("mouseup", function(event) {
    // exit condition 0 - if the prompt has not been submitted
    if (MAIN_RESPONSE_JSON["input_text"] == undefined) {
        return;
    }

    // exit condition 1 - if there is no selection
    var selection_text = window.getSelection().toString();
    if (selection_text.length == 0) {
        document.getElementById("input-text-content").innerHTML = highlight_input_text(
            input_text = MAIN_RESPONSE_JSON["input_text"],
            index_mapping = MAIN_RESPONSE_JSON["input_token_mapping"],
            attentions_per_character = empty_array(MAIN_RESPONSE_JSON["input_text"].length)
        )
        return;
    }

    // exit condition 2 - if the selection is not in the summary text
    var selection_parent_node_id = window.getSelection().anchorNode.parentNode.id;
    if (selection_parent_node_id != "summary-text-content") {
        document.getElementById("input-text-content").innerHTML = highlight_input_text(
            input_text = MAIN_RESPONSE_JSON["input_text"],
            index_mapping = MAIN_RESPONSE_JSON["input_token_mapping"],
            attentions_per_character = empty_array(MAIN_RESPONSE_JSON["input_text"].length)
        )
        return;
    }

    // get the start and end index of the selection
    var selection_start_index = Math.min(window.getSelection().anchorOffset, window.getSelection().focusOffset);
    var selection_end_index = Math.max(window.getSelection().anchorOffset, window.getSelection().focusOffset);

    // get the tokens selected
    var tokens_selected = [];
    for (var i = 0; i < MAIN_RESPONSE_JSON["output_token_mapping"].length; i++) {
        var token_mapping = MAIN_RESPONSE_JSON["output_token_mapping"][i];
        
        var left_overlap = token_mapping[0] >= selection_start_index && token_mapping[0] <= selection_end_index;
        var right_overlap = token_mapping[1] >= selection_start_index && token_mapping[1] <= selection_end_index;
        var outer_overlap = token_mapping[0] <= selection_start_index && token_mapping[1] >= selection_end_index;
        var inner_overlap = token_mapping[0] >= selection_start_index && token_mapping[1] <= selection_end_index;

        if (left_overlap || right_overlap || outer_overlap || inner_overlap) {
            tokens_selected.push(i);
        }
    }

    var min_token_index = Math.min(...tokens_selected);
    var max_token_index = Math.max(...tokens_selected);

    // init empty array for attentions per token and character
    var attentions_per_token = empty_array(MAIN_RESPONSE_JSON["input_token_ids"].length);
    var attentions_per_character = empty_array(MAIN_RESPONSE_JSON["input_text"].length);

    // calculate attentions per token
    for (var i = 0; i < attentions_per_token.length; i++) {
        var attentions_this_token = 0;
        for (var j = min_token_index; j <= max_token_index; j++) {
            attentions_this_token += MAIN_RESPONSE_JSON["cross_attentions"][j][i];
        }

        attentions_per_token[i] = attentions_this_token / (max_token_index - min_token_index + 1);
    }

    // normalize attentions per token
    var max_attention_per_token = Math.max(...attentions_per_token);
    attentions_per_token = attentions_per_token.map(x => x / max_attention_per_token);

    // map attentions per token to attentions per character
    for (var i = 0; i < attentions_per_token.length; i++) {
        var attention = attentions_per_token[i];
        var token_mapping = MAIN_RESPONSE_JSON["input_token_mapping"][i];

        for (var j = token_mapping[0]; j < token_mapping[1]; j++) {
            attentions_per_character[j] = attention;
        }
    }

    // select the mapping
    var user_selected_mapping = document.getElementById("attention-aggregation-granularity").value;
    var mapping_to_use = {
        "tokn": MAIN_RESPONSE_JSON["input_token_mapping"],
        "sent": MAIN_RESPONSE_JSON["input_sentence_mapping"]
    }[user_selected_mapping];

    // update input text
    document.getElementById("input-text-content").innerHTML = highlight_input_text(
        input_text = MAIN_RESPONSE_JSON["input_text"],
        index_mapping = mapping_to_use,
        attentions_per_character = attentions_per_character
    )
});

// ------------------------- HELPER FUNCTIONS -------------------------

function empty_array(length, fill=0) {
    return Array(length).fill(fill);
}

function highlight_input_text(
    input_text,                 // the original input text
    index_mapping,              // a list of [start_index, end_index] pairs for each token / sentence
    attentions_per_character    // a list of attention values for each character in the input text
) {
    var input_text_html = "";

    for (var i = 0; i < index_mapping.length; i++) {
        var index_pair = index_mapping[i];
        var start_index = index_pair[0];
        var end_index = index_pair[1];
        var span_text = input_text.substring(start_index, end_index);

        // add space between words
        if (i != 0 && index_mapping[i - 1][1] != start_index) {
            input_text_html += "<span> </span>";
        }

        // get mean of attentions_per_character between start and end index
        var attention_value = array_mean(attentions_per_character.slice(start_index, end_index));
        var attention_color = "rgba(0, 255, 0, " + attention_value + ")";

        if (start_index != -1) {
            input_text_html += "<span style='background-color: " + attention_color + "'>" + span_text + "</span>";
        }
    }

    return input_text_html;
}

function array_mean(array) {
    var sum = 0;
    for (var i = 0; i < array.length; i++) {
        sum += array[i];
    }
    return sum / array.length;
}
