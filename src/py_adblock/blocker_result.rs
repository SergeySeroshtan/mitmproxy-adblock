use adblock::blocker::BlockerResult as RustBlockerResult;
use pyo3::prelude::*;

#[pyclass]
pub struct BlockerResult {
    #[pyo3(get)]
    pub matched: bool,
    #[pyo3(get)]
    pub important: bool,
    #[pyo3(get)]
    pub redirect: Option<String>,
    #[pyo3(get)]
    rewritten_url: Option<String>,
    #[pyo3(get)]
    pub exception: Option<String>,
    #[pyo3(get)]
    pub filter: Option<String>,
}

impl From<RustBlockerResult> for BlockerResult {
    fn from(br: RustBlockerResult) -> Self {
        Self {
            matched: br.matched,
            important: br.important,
            redirect: br.redirect,
            rewritten_url: br.rewritten_url,
            exception: br.exception,
            filter: br.filter,
        }
    }
}
