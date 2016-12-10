/**
 * Assorted common code for the Instanssi store.
 * @todo Move some of this into a sitewide library?
 */

import Vue from 'vue';
import Promise from 'promise-polyfill';

// Support for this was still a bit patchy last I checked.
let toLocaleStringSupportsOptions = !!(typeof Intl === 'object'
    && Intl && typeof Intl.NumberFormat === 'function');

function formatPriceLocaleString(price) {
    return price.toLocaleString('fi', { style: 'currency', currency: 'EUR'});
}
function formatPriceLegacy(price) {
    return price.toFixed(2) + ' €';
}
let formatPrice;
if(toLocaleStringSupportsOptions) {
    formatPrice = formatPriceLocaleString;
} else {
    formatPrice = formatPriceLegacy;
}

/**
 * Perform an asynchronous HTTP request to a specific method and path,
 * optionally passing some data (not supported for GET requests).
 * @param {string} method - HTTP method, e.g. 'GET'
 * @param {string} path - URL or path to request
 * @param {Object} [data] - Data to pass in the request (encoded into JSON)
 * @returns {Promise.Object} - Result
 */
function storeXHR(method, path, data) {
    return new Promise((resolve, reject) => {
        let xhr = new XMLHttpRequest();
        xhr.onload = function () {
            if(xhr.status >= 200 && xhr.status < 300) {
                resolve(JSON.parse(xhr.responseText));
            } else {
                xhr.onerror();
            }
        };
        xhr.onerror = function () {
            reject(xhr.responseText ? JSON.parse(xhr.responseText) : null);
        };
        xhr.open(method, path);
        xhr.setRequestHeader('Accept', 'application/json');
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.send(data ? JSON.stringify(data) : null);
    });
}

/**
 * Form group with a title, input field and any messages concerning the field.
 */
let storeFormGroup = Vue.component('store-form-group', {
    props: {
        title: String,
        field: String,
        // type: String,
        messages: Object,
        update: Function,
        data: Object
    },
    methods: {
        onInput($event) {
            this.$emit('update', this.field, $event);
        }
    },
    computed: {
        clazz() {
            let { messages, field } = this;
            if(messages && messages[field] && messages[field].length > 0) {
                return 'form-group has-error';
            }
            return 'form-group';
        }
    },
    template: `<div v-bind:class="clazz">
        <label class="col-sm-4 control-label">{{ title }}</label>
        <div class="col-sm-8">
            <input class="form-control" @input="onInput" v-bind:value="data[field]" />
            <store-messages :field="field" :messages="messages" />
        </div>
    </div>`
});

/**
 * Shows messages addressed to a specific named field.
 */
let storeMessages = Vue.component('store-messages', {
    props: {
        /** Field name to pick up messages for. */
        field: String,
        /** Object like { fieldName: [message1, ...] }. */
        messages: Object
    },
    computed: {
        localMessages() {
            let { messages, field } = this;
            if(messages && messages[field] && messages[field].length > 0) {
                return messages[field];
            }
            return null;
        }
    },
    template: `<div><p v-if="localMessages">
        <div class="alert alert-danger" role="alert" v-for="message in localMessages">
            <span class="fa fa-times"></span> {{ message }}
        </div>
    </p></div>`
});

export { formatPrice, storeXHR, storeFormGroup, storeMessages };
