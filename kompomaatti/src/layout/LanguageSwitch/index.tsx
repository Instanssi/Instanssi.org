import React from 'react';
import { observer } from 'mobx-react';
import { action } from 'mobx';

import globalState from 'src/state';
import i18n from 'src/i18n';


@observer
export default class LanguageSwitch extends React.Component<any> {
    @action
    setLanguage(event) {
        globalState.setLanguage(event.target.value);
    }

    get options() {
        return Object.keys(i18n).map(key => (
            { value: key, label: i18n[key].name }
        ));
    }

    get current() {
        return globalState.languageCode;
    }

    render() {
        const { current, options } = this;
        return (
            <select
                className="form-control"
                value={current}
                onChange={this.setLanguage}
            >
                {options.map(option => (
                    <option key={option.value} value={option.value}>
                        {option.label}
                    </option>
                ))}
            </select>
        );
    }
}
