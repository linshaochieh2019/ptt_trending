

const ctx = document.getElementById('myChart').getContext('2d');

let mapping;
fetch('/mapping')
    .then(response => response.json())
    .then(data => {
        mapping = data;
    })
    .catch(error => console.error(error));

let colors;
fetch('/colors')
    .then(response => response.json())
    .then(data => {
        colors = data;
    })
    .catch(error => console.error(error));

fetch('/data')
  .then(response => response.json())
  .then(data => {
    
    console.log(data);

    const datasets = [];
    for (let i = 1; i <= 11; i++){
      const color = colors[i - 1];

      datasets.push({
        label: mapping[i],
        data: data.counts[i],
        backgroundColor: color,
        borderColor: color,
      });
    }

    const chart_data = {
      labels: data['dates'],
      datasets: datasets
    }

    const config = {
      type: 'bar',
      data: chart_data,
      options: {
        plugins: {
          title: {
            display: true,
            text: 'Chart.js Bar Chart - Stacked'
          },
        },
        responsive: true,
        scales: {
          x: {
            stacked: true,
          },
          y: {
            stacked: true,
            ticks: {
              beginAtZero: true
            }
          }
        }
      }
    };

    const myChart = new Chart(ctx, config);
  })
  .catch(error => console.error(error));
