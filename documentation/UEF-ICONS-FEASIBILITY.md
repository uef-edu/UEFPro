# Đánh giá: đưa logo UEF và tên sản phẩm (UEF ID, LMS, Workplace) vào font

> **Cập nhật:** đã có logo vector và đã làm prototype theo Cách B (font phụ `UEF Pro Icons`, xem README). Phần dưới là đánh giá ban đầu.

## Kết luận nhanh

| Hạng mục | Khả thi | Ghi chú |
|---|---|---|
| Logo UEF dạng **đơn sắc** (1 màu, theo màu chữ) | Có | Cần file vector gốc (SVG/AI/EPS). Gán vào vùng Private Use (vd. U+E000). |
| Logo UEF **nhiều màu** (xanh/đỏ/vàng như bản gốc) | Có, nhưng phức tạp | Cần bảng màu COLRv1 hoặc OpenType-SVG. Không được hỗ trợ đồng đều (xem bên dưới). |
| Lockup tên sản phẩm "UEF ID", "LMS", "Workplace" dạng chữ | Có, dễ | Làm bằng ligature từ chữ gõ vào, hoặc glyph PUA riêng. |
| Lockup sản phẩm dạng **badge/pill có nền** | Có | Vẽ glyph riêng (nền bo góc + chữ khoét), đơn sắc. |
| Icon UI chung (home, user, lock...) | Có | Nên dùng icon font/SVG riêng; không đưa vào font chữ chính. |

## Rào cản hiện tại

1. **Chưa có vector logo UEF.** Trên uef.edu.vn chỉ có `logo-uef-home.jpg` (137×129 px, nhiều màu). Không thể dùng làm outline cho font. Cần xin bộ nhận diện thương hiệu (SVG/AI) từ phòng Truyền thông/Marketing. Không nên tự trace từ JPG nhỏ vì sai lệch nhận diện thương hiệu.
2. **Font đơn sắc vs logo nhiều màu.** Glyph thường chỉ lấy màu chữ hiện tại. Logo nhiều màu cần COLRv1 (Chrome, Edge, Firefox mới; Safari chưa đầy đủ) hoặc OpenType-SVG (Safari, Firefox; Chrome không hỗ trợ). Nếu cần chạy mọi nơi, nên dùng bản đơn sắc + fallback ảnh/SVG.
3. **Kích thước nhỏ.** Logo UEF có tòa tháp chi tiết nhỏ và dòng chữ tiếng Việt; dưới ~24 px cần phiên bản đơn giản hóa riêng (chỉ chữ "UEF" hoặc biểu tượng rút gọn).
4. **Giấy phép/thương hiệu.** OFL 1.1 cho phép bản fork này. Tuy nhiên, logo là tài sản nhãn hiệu của UEF: nếu repo công khai, mọi người có thể tải và nhúng logo trong font. Cân nhắc để glyph logo trong một bản build nội bộ riêng, hoặc chấp nhận công khai có chủ đích.
5. **Truy cập/SEO/accessibility.** Glyph PUA không có nghĩa với trình đọc màn hình. Cần `aria-label`/`aria-hidden` khi dùng. Ligature từ chữ thật (ví dụ gõ `UEF ID`) giữ được văn bản gốc nên tốt hơn.

## Khuyến nghị thiết kế

- Giữ font chữ chính **sạch**, thêm icon qua một trong hai cách:
  - **Cách A (đơn giản, khuyến nghị bắt đầu):** glyph PUA đơn sắc trong chính UEF Pro: `U+E000` logo UEF rút gọn, `U+E001` UEF ID, `U+E002` LMS, `U+E003` Workplace. Kèm ligature tùy chọn (feature `liga`/`calt`) để gõ `UEF ID` ra lockup.
  - **Cách B:** tách thành font phụ `UEF Pro Icons` (đơn sắc + bản COLRv1), dùng chung với UEF Pro qua CSS `font-family: "UEF Pro", "UEF Pro Icons"`. Dễ cập nhật độc lập khi logo/sản phẩm đổi.
- Lockup sản phẩm nên căn theo cap-height và baseline của UEF Pro, để chạy cùng dòng chữ không lệch.
- Thêm biến thể weight (ít nhất Regular/Bold) cho glyph logo nếu muốn khớp variable font; nếu không, đặt cùng outline mọi weight.

## Việc cần để tiếp tục

1. Logo UEF vector (SVG/AI/EPS), cả bản màu và bản đơn sắc.
2. Xác nhận danh sách sản phẩm cần lockup, kiểu hiển thị (chữ thuần / badge) và tên chính thức (UEF ID, LMS, Workplace, thêm gì khác?).
3. Quyết định repo công khai hay riêng tư (ảnh hưởng việc để logo trong font).
4. Chọn Cách A hay B.
