function executeCommand (command) {
	pywebview.api.execute_command(command);
}

function loadModule (module_name) {
	pywebview.api.get_module_webview(module_name).then(function(response){
		$('#moduleSettingsContainer').empty();

		var webview = response['webview'];
		var module_data = response['module_data'];

		if ('actions' in webview) {
			var action_bar = $('<div>', {'class': 'actions'});
			for (action in webview['actions']) {
				action_bar.append($('<button>', {
					'onclick': `executeCommand('${webview['actions'][action]}')`,
					'text': action
				}));
			}
			$('#moduleSettingsContainer').append(action_bar);
		}

		if ('tabular-data' in webview) {
			for (table_name in webview['tabular-data']) {
				var webview_table = webview['tabular-data'][table_name];
				$('#moduleSettingsContainer').append($('<div>', {
					'class': 'tableTitle',
					'text': webview['tabular-data'][table_name]['title']
				}));

				var table = $('<table>', {'class': 'tableView'});
				var table_header = $('<tr>');
				for (column_index in webview_table['columns']) {
					var column_name = webview_table['columns'][column_index];
					var column_detail = webview_table['column-detail'][column_name];
					table_header.append($('<th>').text(column_detail['title']));
				}
				if ('row-actions' in webview_table) {
					table_header.append($('<th>').text('Actions'));
				}
				table.append(table_header);

				for (row_data_index in module_data[table_name]) {
					var row_data = module_data[table_name][row_data_index];
					var row = $('<tr>');
					for (column_index in webview_table['columns']) {
						var column_name = webview_table['columns'][column_index];
						var data_type = webview_table['column-detail'][column_name]['type'];
						var value = row_data[column_name];

						if (data_type == 'bool') {
							if (value) { value = 'Yes'; }
							else { value = 'No'; }
						}

						row.append($('<td>').text(value));
					}

					if ('row-actions' in webview_table) {
						var select = $('<select>');
						select.append($('<option>'));
						for (row_action_index in webview_table['row-actions']) {
							var row_action_name = webview_table['row-actions'][row_action_index];
							var row_action_detail = webview_table['action-detail'][row_action_name];
							select.append($('<option>', {'value': row_action_name}).text(row_action_detail['title']));
						}
						row.append($('<td>').append(select));
					}
					table.append(row);
				}
				$('#moduleSettingsContainer').append(table);
			}
		}
	})
}
window.addEventListener('pywebviewready', function() {
	pywebview.api.init();
	pywebview.api.get_module_list().then(function(response) {
		for (module in Object.keys(response).sort()) {
			var module_name = response[module]['module_name'];
			$('#navigationContainer').append(
				$('<div>', {
					'class': 'moduleButton'
				}).append(
					$('<button>', {
						'onclick': `loadModule('${module_name}')`,
						'text': module_name
					})
				)
			);

		}
	})
});
