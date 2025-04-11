use crate::py_adblock::BlockerResult as AdblockBlockerResult;
use crate::py_adblock::FilterSet as AdblockFilterSet;
use adblock::request::Request as AdblockRequest;
use adblock::Engine as AdblockEngine;
use pyo3::prelude::*;
use scraper::{Html, Selector};

#[pyclass(unsendable)]
pub struct Engine {
    engine: AdblockEngine,
}

#[pymethods]
impl Engine {
    #[new]
    fn new() -> Self {
        let engine = AdblockEngine::default();
        Self { engine }
    }

    #[staticmethod]
    pub fn from_filter_set(set: &AdblockFilterSet, optimize: bool) -> Self {
        let engine = AdblockEngine::from_filter_set(set.filter_set.clone(), optimize);
        Self { engine }
    }

    #[pyo3(signature = (url, source_url, request_resource_type = "other"))]
    pub fn check_network_request(
        &self,
        url: &str,
        source_url: &str,
        request_resource_type: &str,
    ) -> PyResult<AdblockBlockerResult> {
        let request = AdblockRequest::new(url, source_url, request_resource_type);
        if let Err(e) = request {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "Invalid request: {}",
                e
            )));
        }
        let request = request.unwrap();
        let result = self.engine.check_network_request(&request);

        Ok(AdblockBlockerResult::from(result))
    }

    pub fn cleanup_html(&self, url: &str, original_html: &str) -> PyResult<String> {
        let mut filtered_html = original_html.to_string();
        let html_doc = Html::parse_document(&original_html);

        println!("=== Remove blocked <script> elements ===");
        let script_selector = Selector::parse("script").unwrap();
        for script in html_doc.select(&script_selector) {
            if let Some(src) = script.value().attr("src") {
                let request = AdblockRequest::new(src, "http://localhost", "script");
                if let Err(e) = request {
                    println!("Invalid request: {}", e);
                    continue;
                }
                let result = self.engine.check_network_request(&request.unwrap());
                if result.matched {
                    println!("Blocked script: {}", src);
                    let tag_html = script.html();
                    filtered_html = filtered_html.replace(&tag_html, "");
                }
            }
        }

        println!("=== Inject <style> block for cosmetic filtering ===");
        let resources = self.engine.url_cosmetic_resources(url);
        let mut css_selectors = Vec::new();
        let hide_selectors = resources.hide_selectors;
        for selector in hide_selectors {
            css_selectors.push(selector);
        }

        if !css_selectors.is_empty() {
            let style_block = format!(
                "<style>{}</style>",
                css_selectors
                    .iter()
                    .map(|s| format!("{} {{ display: none !important; }}", s))
                    .collect::<Vec<_>>()
                    .join("\n")
            );

            // Insert style tag just before </head>
            filtered_html = filtered_html.replace("</head>", &format!("{}\n</head>", style_block));
        }

        Ok(filtered_html)
    }
}
