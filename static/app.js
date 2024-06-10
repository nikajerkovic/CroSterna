function resetFormAndHideResult() {
            var resultDiv = document.getElementById('resultDiv');
            if (resultDiv) {
                resultDiv.style.display = 'none'; // Hide the result div
            }
            var warningDiv = document.getElementById('warning');
            if (warningDiv) {
                warningDiv.style.display = 'none'; // Hide the warning message
            }
            var inputs = document.querySelectorAll('.input-container input');
            inputs.forEach(input => {
                if (input.type === 'number' || input.type === 'text') {
                    input.value = ''; // Clear the value
                }
            });
        }

$(document).ready(function () {
            $('form').on('submit', function (event) {
                event.preventDefault(); // Prevent default form submission
                $.ajax({
                    type: 'POST',
                    url: '/',
                    data: $(this).serialize(), // Serialize the form data
                    success: function (response) {
                        if (response.warning) {
                            $('#warning').text(response.warning).show();
                            document.getElementById('warning').scrollIntoView({ behavior: 'smooth' });
                            $('#resultDiv').hide();
                        } else if (response.error) {
                            $('#warning').text(response.error).show();
                             document.getElementById('warning').scrollIntoView({ behavior: 'smooth' });
                            $('#resultDiv').hide();
                        } else {
                            $('#warning').hide();
                            $('#resultDiv').show();
                            $('#adjusted_lower').text(response.adjusted_lower);
                            $('#adjusted_upper').text(response.adjusted_upper);
                            $('.timeline-bar').css('left', response.lower_bound_percentage + '%').css('width', response.range_width_percentage + '%');
                            $('.timeline-marker.lower').css('left', response.lower_bound_percentage + '%');
                            $('.timeline-marker.upper').css('left', response.upper_bound_percentage + '%');
                            $('.marker-label.lower').css('left', response.lower_bound_percentage + '%').text(response.adjusted_lower);
                            $('.marker-label.upper').css('left', response.upper_bound_percentage + '%').text(response.adjusted_upper);
                        }

                         // Scroll to the resultDiv
                        
                        document.getElementById('resultDiv').scrollIntoView({ behavior: 'smooth' });

                    },
                    error: function (error) {
                        console.log(error);
                    }
                });
            });
        });