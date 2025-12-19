using Microsoft.AspNetCore.Mvc;

using System.Diagnostics;

using WebApp_TT_QualityDataset.Models;

using System.IO;
using System.Web;
using System.Security.Cryptography.X509Certificates;
using System.Data;
using System.Linq;
using System.Collections.Generic;
using Newtonsoft.Json;
using System.Text.Json.Serialization;



namespace WebApp_TT_QualityDataset.Controllers
{
    public class HomeController : Controller
    {
        private readonly ILogger<HomeController> _logger;

        public HomeController(ILogger<HomeController> logger)
        {
            _logger = logger;
        }

        public IActionResult Index()
        {
            return View();
        }

        [HttpPost]
        public IActionResult ListFiles(string directoryPath)
        {
            if (Directory.Exists(directoryPath))
            {
                var files = Directory.GetFiles(directoryPath);
                ViewBag.Files = files;
                ViewBag.DirectoryPath = directoryPath;
            }
            else
            {
                ViewBag.Error = "El file no encontrado";
            }
            return View("Index");
        }

        public IActionResult ReadFile(string filePath)
        {
            if (System.IO.File.Exists(filePath))
            {
                try
                {
                    string fileContent = System.IO.File.ReadAllText(filePath);
                    ViewBag.FileContent = fileContent;
                    ViewBag.FilePath = filePath;
                }
                catch (Exception ex)
                {
                    ViewBag.Error = $"Error al leer el archivo: {ex.Message}";
                }
            }
            else
            {
                ViewBag.Error = "El file no existe";
            }
            return View();
        }

        public IActionResult VisualizeData(string filePath, string[] columns)
        {
            ViewBag.ImagePaths = new List<string>();

            if (System.IO.File.Exists(filePath))
            {
                try
                {
                    if (columns == null || columns.Length == 0)
                    {
                    
                        var avaliableColumns = GetAvailableColums(filePath);
                        ViewBag.Columns = avaliableColumns;
                        ViewBag.SelectedColumns = columns;
                        ViewBag.FilePath = filePath;
                        ViewBag.FileName = Path.GetFileName(filePath);
                    }
                    else
                    {
                        //ViewBag.Error = "No se han seleccionado columnas.";
                        //return View();
                        var avaliableColumns = GetAvailableColums(filePath);
                        ViewBag.Columns = avaliableColumns;
                        ViewBag.SelectedColumns = columns;
                        ViewBag.FilePath = filePath;
                        ViewBag.FileName = Path.GetFileName(filePath);
                    }

                    var imagesPaths = new List<string>
                        {
                            "wwwroot/images/clusters.png",
                            "wwwroot/images/correlation_matrix.png",
                            "wwwroot/images/pairplot.png",
                            "wwwroot/images/distribucion.png"
                        };

                    foreach (var imagePath in imagesPaths)
                    {
                        if (System.IO.File.Exists(imagePath))
                        {
                            System.IO.File.Delete(imagePath);
                        }
                    }

                    // Llama script Python
                    var psi = new ProcessStartInfo
                    {
                        FileName = "python",
                        Arguments = $"\"C:\\Users\\Xxx\\source\\repos\\WebApp_TT_QualityDataset\\WebApp_TT_QualityDataset\\Python\\GraficoDatos.py\" \"{filePath}\"",
                        UseShellExecute = false,
                        CreateNoWindow = true,
                        RedirectStandardError = true,
                        RedirectStandardOutput = true
                    };

                    var process = Process.Start(psi);
                    process.WaitForExit();

                    var output = process.StandardOutput.ReadToEnd();
                    var error = process.StandardError.ReadToEnd();

                    if (!string.IsNullOrEmpty(error))
                    {
                        ViewBag.Error = error;
                        _logger.LogError($"Error al ejecutar el script de Python: {error}");
                        return View();
                    }

                    _logger.LogInformation($"\n ******** Salida del script de Python: {output}");

                    // Verificar si nuevas imágenes se han generado
                    foreach (var imagePath in imagesPaths)
                    {
                        var webPath = "/" + imagePath.Replace("wwwroot/", "");
                        if (System.IO.File.Exists(imagePath))
                        {
                            ViewBag.ImagePaths.Add(webPath);
                            _logger.LogInformation($"Ruta imagen añadida: {webPath}");
                        }
                        else
                        {
                            _logger.LogWarning($"Imagen no encontrada: {imagePath}");
                        }
                    }

                    ViewBag.FileName = Path.GetFileName(filePath);



                    

                }
                catch (Exception ex)
                {
                    ViewBag.Error = $"Error al ejecutar el script de Python: {ex.Message}";
                    _logger.LogError(ex, "Error al ejecutar el script de Python");
                }
            }
            else
            {
                ViewBag.Error = "Error en Input.";
            }

            _logger.LogInformation($"ViewBag.ImagePaths contiene {ViewBag.ImagePaths.Count} elementos.");
            return View();
        }

        private List<string> GetAvailableColums(string filePath)
        {
            var columns = new List<string>();
            if (System.IO.File.Exists(filePath))
            {
                try
                {
                    var fileContent = System.IO.File.ReadAllText(filePath);
                    var dt = ConvertCSVtoDataTable(fileContent);
                    if (dt != null)
                    {
                        columns = dt.Columns.Cast<DataColumn>().Select(x => x.ColumnName).ToList();
                    }
                }
                catch (Exception ex)
                {
                    ViewBag.Error = $"Error al leer el archivo: {ex.Message}";
                    _logger.LogError(ex, "Error al leer el archivo");
                }
            }
            else
            {
                ViewBag.Error = "El archivo no existe";
            }
            return columns;
        }

        private static DataTable ConvertCSVtoDataTable(string csvData)
        {
            DataTable dt = new();
            string[] rows = csvData.Split('\n');

            if (rows.Length > 0)
            {
                // Columnas
                string[] columns = rows[0].Split(',');
                foreach (string column in columns)
                {
                    dt.Columns.Add(column.Trim());
                }

                // Filas
                for (int i = 1; i < rows.Length; i++)
                {
                    string[] rowValues = rows[i].Split(',');
                    if (rowValues.Length == columns.Length)
                    {
                        DataRow dr = dt.NewRow();
                        for (int j = 0; j < columns.Length; j++)
                        {
                            dr[j] = rowValues[j].Trim();
                        }
                        dt.Rows.Add(dr);
                    }
                }
            }
            return dt;
        }

        public IActionResult Privacy()
        {
            return View();
        }

        [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
        public IActionResult Error()
        {
            return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
        }
    }
}
