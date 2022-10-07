$(document).ready(function() {

    $('#srcForm').on('submit', function(event) {

        $.ajax({
            data: {
                srcIP: $('#srcIPInput').val(),
                srcPath: $('#srcPathInput').val()
            },
            type: 'POST',
            url: '/updateSrc'
        })
        .done(function(data) {

            const tableData = document.getElementById("srcTable")
            tableData.textContent = ''

            data.files.forEach(file => {

                const newTableEntry = document.createElement("tr")
                const newCheckBox = document.createElement("td")
                const newFileName = document.createElement("td")
                const newFileLastMod = document.createElement("td")
                const newFileSize = document.createElement("td")

                newCheckBox.innerHTML = '<input type="checkbox" id="fileSelect" name="fileSelect" value="' + file.name + '">'
                const nameContent = document.createTextNode(file.name)
                const lastModContent = document.createTextNode(file.last_modified)
                const sizeContent = document.createTextNode(file.size + " B")

                newFileName.appendChild(nameContent)
                newFileLastMod.appendChild(lastModContent)
                newFileSize.appendChild(sizeContent)
                
                newTableEntry.appendChild(newCheckBox)
                newTableEntry.appendChild(newFileName)
                newTableEntry.appendChild(newFileLastMod)
                newTableEntry.appendChild(newFileSize)
                
                $('#srcTable').append(newTableEntry)
                // console.log(file.name)
            })

            $('#srcFileDisplay').show()
        });
        event.preventDefault()
    });

    $('#destForm').on('submit', function(event) {

        $.ajax({
            data: {
                destIP: $('#destIPInput').val(),
                destPath: $('#destPathInput').val()
            },
            type: 'POST',
            url: '/updateDest'
        })
        .done(function(data) {

            const tableData = document.getElementById("destTable")
            tableData.textContent = ''

            data.files.forEach(file => {

                const newTableEntry = document.createElement("tr")
                const newFileName = document.createElement("td")
                const newFileLastMod = document.createElement("td")
                const newFileSize = document.createElement("td")
                const newBlank = document.createElement("td")

                const nameContent = document.createTextNode(file.name)
                const lastModContent = document.createTextNode(file.last_modified)
                const sizeContent = document.createTextNode(file.size + " B")

                newFileName.appendChild(nameContent)
                newFileLastMod.appendChild(lastModContent)
                newFileSize.appendChild(sizeContent)
                
                newTableEntry.appendChild(newBlank)
                newTableEntry.appendChild(newFileName)
                newTableEntry.appendChild(newFileLastMod)
                newTableEntry.appendChild(newFileSize)
                
                $('#destTable').append(newTableEntry)
                // console.log(file.name)
            })

            $('#destFileDisplay').show()
        });
        event.preventDefault()
    });

    $('#transferFilesForm').submit(function(event) {
        let checkboxes = document.querySelectorAll('input[name="fileSelect"]:checked');
        let values = [];
        checkboxes.forEach((checkbox) => {
            values.push(checkbox.value);
        });
        
        $.ajax({
            data: {
                srcIP: $('#srcIPInput').val(),
                srcPath: $('#srcPathInput').val(),
                destIP: $('#destIPInput').val(),
                destPath: $('#destPathInput').val(),
                selectedFiles: values
            },
            type: 'POST',
            url: '/transferFiles'
        })
        .done(function(data) {
            console.log(data)
            location.href = "/history"
        });
        
        event.preventDefault()
    });
});
