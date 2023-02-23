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

            // data.files.forEach(file => {

            //     const newTableEntry = document.createElement("tr")
            //     const newCheckBox = document.createElement("td")
            //     const newFileName = document.createElement("td")
            //     const newFileLastMod = document.createElement("td")
            //     const newFileSize = document.createElement("td")

            //     newCheckBox.innerHTML = '<input type="checkbox" id="fileSelect" name="fileSelect" value="' + file.name + '">'
            //     const nameContent = document.createTextNode(file.name)
            //     const lastModContent = document.createTextNode(file.last_modified)
            //     const sizeContent = document.createTextNode(file.size + " B")

            //     newFileName.appendChild(nameContent)
            //     newFileLastMod.appendChild(lastModContent)
            //     newFileSize.appendChild(sizeContent)
                
            //     newTableEntry.appendChild(newCheckBox)
            //     newTableEntry.appendChild(newFileName)
            //     newTableEntry.appendChild(newFileLastMod)
            //     newTableEntry.appendChild(newFileSize)
                
            //     $('#srcTable').append(newTableEntry)
                // console.log(file.name)
            // })

            console.log(data)
            // data.files.forEach(file => {
            const newTableEntry = document.createElement("tr")
            const newCheckBox = document.createElement("td")
            const newFileName = document.createElement("td")
            const newFileLastMod = document.createElement("td")
            const newFileSize = document.createElement("td")

            newCheckBox.innerHTML = '<input type="checkbox" id="fileSelect" name="fileSelect" value="' + data + '">'
            const nameContent = document.createTextNode(data.files)
            const lastModContent = document.createTextNode(null)
            const sizeContent = document.createTextNode(null)
        
            newFileName.appendChild(nameContent)
            newFileLastMod.appendChild(lastModContent)
            newFileSize.appendChild(sizeContent)
            
            newTableEntry.appendChild(newCheckBox)
            newTableEntry.appendChild(newFileName)
            newTableEntry.appendChild(newFileLastMod)
            newTableEntry.appendChild(newFileSize)
            
            $('#srcTable').append(newTableEntry)

            // })
            
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

            // data.files.forEach(file => {

            //     const newTableEntry = document.createElement("tr")
            //     const newFileName = document.createElement("td")
            //     const newFileLastMod = document.createElement("td")
            //     const newFileSize = document.createElement("td")
            //     const newBlank = document.createElement("td")

            //     const nameContent = document.createTextNode(file.name)
            //     const lastModContent = document.createTextNode(file.last_modified)
            //     const sizeContent = document.createTextNode(file.size + " B")

            //     newFileName.appendChild(nameContent)
            //     newFileLastMod.appendChild(lastModContent)
            //     newFileSize.appendChild(sizeContent)
                
            //     newTableEntry.appendChild(newBlank)
            //     newTableEntry.appendChild(newFileName)
            //     newTableEntry.appendChild(newFileLastMod)
            //     newTableEntry.appendChild(newFileSize)
                
            //     $('#destTable').append(newTableEntry)
            //     // console.log(file.name)
            // })

            console.log(data)
            // data.files.forEach(file => {
            const newTableEntry = document.createElement("tr")
            const newCheckBox = document.createElement("td")
            const newFileName = document.createElement("td")
            const newFileLastMod = document.createElement("td")
            const newFileSize = document.createElement("td")

            newCheckBox.innerHTML = '<input type="checkbox" id="fileSelect" name="fileSelect" value="' + data + '">'
            const nameContent = document.createTextNode(data.files)
            const lastModContent = document.createTextNode(null)
            const sizeContent = document.createTextNode(null)
        
            newFileName.appendChild(nameContent)
            newFileLastMod.appendChild(lastModContent)
            newFileSize.appendChild(sizeContent)
            
            newTableEntry.appendChild(newCheckBox)
            newTableEntry.appendChild(newFileName)
            newTableEntry.appendChild(newFileLastMod)
            newTableEntry.appendChild(newFileSize)
            
            $('#destTable').append(newTableEntry)

            // })

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

    // srcIP
    $('#site1_IP_form').on('submit', function(event) {
        console.log("calling js")
        $.ajax({
            data: {
                site1_IP: $('#site1_IP_input').val(),
            },
            type: 'POST',
            url: '/site1_ip'
        })
        .done(function(data) {
            console.log(data)

            if (!data.is_valid_ip) {
                alert("IP not found in database")
                const site1_details = document.getElementById("site1_details")
                const newP = document.createElement("p")
                newP.append("Invalid IP Address")
                site1_details.replaceChildren(newP)
            } else {
                const site1_details = document.getElementById("site1_details")
                const newP = document.createElement("p")
                newP.append("Valid IP Address")
                site1_details.replaceChildren(newP)
            }
        })
        event.preventDefault()

    });

    // destIP
    $('#site2_IP_form').on('submit', function(event) {
        console.log("calling js")
        $.ajax({
            data: {
                site2_IP: $('#site2_IP_input').val(),
            },
            type: 'POST',
            url: '/site2_ip'
        })
        .done(function(data) {
            console.log(data)

            if (!data.is_valid_ip) {
                alert("IP not found in database")
                const site2_details = document.getElementById("site2_details")
                const newP = document.createElement("p")
                newP.append("Invalid IP Address")
                site2_details.replaceChildren(newP)
            } else {
                const site2_details = document.getElementById("site2_details")
                const newP = document.createElement("p")
                newP.append("Valid IP Address")
                site2_details.replaceChildren(newP)
            }
        })
        event.preventDefault()

    });

})
