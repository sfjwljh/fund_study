$(document).ready(function() {
    let usedLevel2Values = new Set();
    let saveTimeout = null;
    let allEntities = []; // 存储所有实体数据

    // 预定义的选项
    const LEVEL1_OPTIONS = [
        '无关',
        '上游产业情况',
        '下游产业情况',
        '行业自身情况',
        '国家政策方向',
        '宏观市场'
    ];

    const TIME_ATTR_OPTIONS = [
        '始终',
        '过去',
        '现在',
        '未来'
    ];

    const SCORE_OPTIONS = ['-2', '-1', '0', '1', '2'];

    // 创建选择框 HTML
    function createSelectOptions(options, value) {
        return options.map(option => 
            `<option value="${option}" ${option === value ? 'selected' : ''}>${option}</option>`
        ).join('');
    }

    // 自动保存函数
    function autoSave(callback) {
        let selectedSentence = $('.sentence-item.selected');
        if (selectedSentence.length === 0) {
            if (callback) callback();
            return;
        }

        let sentenceId = selectedSentence.data('id');
        let entities = [];
        
        // 获取当前显示的表单的实体数据
        $(`#entity-form-${sentenceId} .entity-input`).each(function() {
            let entity = {
                industry: $(this).find('.industry-input').val(),
                level1: $(this).find('.level1-input').val(),
                level2: $(this).find('.level2-input').val(),
                time_attr: $(this).find('.time-attr-input').val(),
                score: $(this).find('.score-input').val(),
                status: $(this).find('.status-input').val(),
                doubt_remark: $(this).find('.doubt-input').val()
            };
            if (entity.level2) {
                usedLevel2Values.add(entity.level2);
            }
            entities.push(entity);
        });

        // 检查是否有存疑备注和标注
        let hasDoubt = entities.some(entity => 
            entity.doubt_remark && entity.doubt_remark.trim() !== ''
        );
        let hasLabels = entities.some(entity => 
            entity.level1 || entity.level2 || entity.status
        );
        
        // 更新句子容器的状态
        let sentenceContainer = selectedSentence.closest('.sentence-container');
        let markersContainer = selectedSentence.find('.markers-container');
        
        if (markersContainer.length === 0) {
            markersContainer = $('<div class="markers-container"></div>');
            selectedSentence.append(markersContainer);
        }
        
        markersContainer.empty();
        if (hasDoubt) markersContainer.append('<span class="doubt-marker">存疑</span>');
        if (hasLabels) markersContainer.append('<span class="label-marker">已标注</span>');
        
        sentenceContainer.toggleClass('has-doubt', hasDoubt);
        sentenceContainer.toggleClass('has-labels', hasLabels);

        if (allEntities[sentenceId]) {
            allEntities[sentenceId].entities = entities;
        }

        $.ajax({
            url: '/save_entities',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                sentence_id: sentenceId,
                entities: entities
            }),
            success: function(response) {
                console.log('保存成功');
                if (callback) callback();
            },
            error: function(error) {
                console.error('保存失败:', error);
                if (callback) callback();
            }
        });
    }

    function debouncedSave() {
        if (saveTimeout) {
            clearTimeout(saveTimeout);
        }
        saveTimeout = setTimeout(autoSave, 500);
    }

    // 获取指定 level2 值对应的所有 status
    function getStatusesByLevel2(level2) {
        let statuses = new Set();
        // 只从当前文档的数据中收集status
        allEntities.forEach(sentence => {
            if (sentence && sentence.entities) {
                sentence.entities.forEach(entity => {
                    if (entity.level2 === level2 && entity.status) {
                        statuses.add(entity.status.trim());
                    }
                });
            }
        });
        return Array.from(statuses);
    }

    // 修改过滤建议列表函数
    function filterSuggestions(input, values, keyword) {
        let filteredValues = values.filter(value => 
            value.toLowerCase().includes(keyword.toLowerCase())
        );
        
        // 移除所有现有的建议列表
        $('.suggestion-list').remove();
        
        if (filteredValues.length > 0) {
            // 创建新的建议列表
            let suggestionList = $('<div class="suggestion-list"></div>');
            
            // 添加建议项
            filteredValues.forEach(value => {
                suggestionList.append(`<div class="suggestion-item">${value}</div>`);
            });

            // 将建议列表添加到输入框的父容器中
            input.parent().append(suggestionList);

            // 获取输入框的位置和尺寸
            let inputPos = input.position();
            let inputHeight = input.outerHeight();

            // 设置建议列表的位置和宽度
            suggestionList.css({
                position: 'absolute',
                top: inputPos.top + inputHeight + 'px',
                left: inputPos.left + 'px',
                width: input.outerWidth() + 'px',
                'z-index': 1000
            });
        }
    }

    // 修改查找相同 level2 的最近 level1 值的函数
    function findLastLevel1ForLevel2(level2) {
        console.log('正在查找level2值:', level2);
        
        // 先在当前表单中查找
        let currentForm = $('.entity-form.active');
        let currentInputs = currentForm.find('.entity-input');
        
        // 从后向前遍历当前表单中的所有实体
        for (let i = currentInputs.length - 1; i >= 0; i--) {
            let entity = currentInputs.eq(i);
            let entityLevel2 = entity.find('.level2-input').val();
            let entityLevel1 = entity.find('.level1-input').val();
            
            if (entityLevel2 === level2 && entityLevel1) {
                console.log('在当前表单中找到匹配:', entityLevel1);
                return entityLevel1;
            }
        }

        // 如果当前表单中没找到，再查找历史数据
        // 从后向前遍历所有句子（最新的句子在后面）
        for (let i = allEntities.length - 1; i >= 0; i--) {
            let sentence = allEntities[i];
            if (sentence && sentence.entities) {
                // 从后向前遍历每个句子中的实体
                for (let j = sentence.entities.length - 1; j >= 0; j--) {
                    let entity = sentence.entities[j];
                    if (entity.level2 === level2 && entity.level1) {
                        console.log('在历史数据中找到匹配:', entity.level1);
                        return entity.level1;
                    }
                }
            }
        }

        console.log('没有找到匹配的 level1');
        return null;
    }

    // 修改 level2 输入框的事件处理，添加更多日志
    $(document).on('input', '.level2-input', function() {
        let keyword = $(this).val();
        let level1Input = $(this).closest('.entity-input').find('.level1-input');
        
        console.log('level2输入变化:', keyword);
        console.log('当前level1值:', level1Input.val());
        
        // 如果 level2 有值但 level1 为空，尝试自动填充 level1
        if (keyword && !level1Input.val()) {
            console.log('尝试查找匹配的level1值');
            let lastLevel1 = findLastLevel1ForLevel2(keyword);
            if (lastLevel1) {
                console.log('找到匹配的level1值，正在填充:', lastLevel1);
                level1Input.val(lastLevel1);
            }
        }

        filterSuggestions($(this), Array.from(usedLevel2Values), keyword);
        debouncedSave();
    });

    // 为 status 输入框添加实时索
    $(document).on('input', '.status-input', function() {
        let keyword = $(this).val();
        let level2Value = $(this).closest('.entity-input').find('.level2-input').val();
        if (level2Value) {
            let relevantStatuses = getStatusesByLevel2(level2Value);
            filterSuggestions($(this), relevantStatuses, keyword);
        }
        debouncedSave();
    });

    // 其他输入框只需要自动保存
    $(document).on('input', '.level1-input, .doubt-input', function() {
        debouncedSave();
    });

    // 添加函数：从所有数据中收集已使用的值
    function collectHistoricalValues(data) {
        // 清空之前的值，确保只包含当前文档的推荐
        usedLevel2Values.clear();
        
        data.forEach(item => {
            if (item.entities && Array.isArray(item.entities)) {
                item.entities.forEach(entity => {
                    if (entity.level2 && entity.level2.trim() !== '') {
                        usedLevel2Values.add(entity.level2.trim());
                    }
                });
            }
        });
    }

    // 修改 loadSentences 函数
    function loadSentences() {
        let currentSelectedId = $('.sentence-item.selected').data('id');
        
        return $.get('/get_sentences', function(data) {
            allEntities = data;
            
            // 在加载句子列表之前收集历史值
            collectHistoricalValues(data);
            
            let sentenceList = $('#sentence-list');
            sentenceList.empty();
            
            if (!data || data.length === 0) {
                sentenceList.append('<p>暂无数据</p>');
                return;
            }

            // 创建句子容器和标注区域
            data.forEach((item, index) => {
                let isSelected = (index === currentSelectedId) ? 'selected' : '';
                
                // 检查是否有存疑备注和标注
                let hasDoubt = false;
                let hasLabels = false;
                if (item.entities && item.entities.length > 0) {
                    hasDoubt = item.entities.some(entity => 
                        entity.doubt_remark && entity.doubt_remark.trim() !== ''
                    );
                    hasLabels = item.entities.some(entity => 
                        entity.level1 || entity.level2 || entity.status
                    );
                }

                // 创建标记容器
                let markers = [];
                if (hasDoubt) markers.push('<span class="doubt-marker">存疑</span>');
                if (hasLabels) markers.push('<span class="label-marker">已标注</span>');
                let markersHtml = markers.length ? `<div class="markers-container">${markers.join('')}</div>` : '';

                let container = $(`
                    <div class="sentence-container ${hasDoubt ? 'has-doubt' : ''} ${hasLabels ? 'has-labels' : ''}">
                        <div class="sentence-item ${isSelected}" data-id="${index}">
                            ${item.sentence || '空句子'}
                            ${markersHtml}
                        </div>
                        <div class="entity-form ${isSelected ? 'active' : ''}" id="entity-form-${index}">
                            <!-- 实体表单将在点击时动态加载 -->
                        </div>
                    </div>
                `);
                sentenceList.append(container);
            });

            // 如果有选中的句子，加载其实体表单
            if (currentSelectedId !== undefined && currentSelectedId !== null) {
                loadEntityForm(currentSelectedId);
            }
        }).fail(function(error) {
            console.error('加载句子列表失败:', error);
            $('#sentence-list').append('<p>加载失败，请刷新页面重试</p>');
        });
    }

    // 修改点击句子的处理函数，添加强制保存
    $(document).on('click', '.sentence-item', function() {
        // 先保存当前正在编辑的句子
        if (saveTimeout) {
            clearTimeout(saveTimeout);
            saveTimeout = null;
            autoSave(() => {
                let sentenceId = $(this).data('id');
                $('.sentence-item').removeClass('selected');
                $('.entity-form').removeClass('active');
                $(this).addClass('selected');
                $(`#entity-form-${sentenceId}`).addClass('active');
                loadEntityForm(sentenceId);
            });
        } else {
            let sentenceId = $(this).data('id');
            $('.sentence-item').removeClass('selected');
            $('.entity-form').removeClass('active');
            $(this).addClass('selected');
            $(`#entity-form-${sentenceId}`).addClass('active');
            loadEntityForm(sentenceId);
        }
    });

    // 新增加载实体表单的函数
    function loadEntityForm(sentenceId) {
        $.get(`/get_entities/${sentenceId}`, function(entities) {
            let entityForm = $(`#entity-form-${sentenceId}`);
            entityForm.empty();
            
            if (!entities || entities.length === 0) {
                entities = [{ level1: '', level2: '', time_attr: '', score: '', status: '', doubt_remark: '' }];
            }
            
            entities.forEach((entity, index) => {
                let entityInput = $(createEntityInput(entity, index));
                entityForm.append(entityInput);
                // 检查新创建��实体是否需要自动填充行业
                autoFillIndustry(entityInput);
            });

            entityForm.append(`
                <div class="entity-controls">
                    <button class="add-entity-btn">添加新实体</button>
                </div>
            `);
        });
    }

    loadSentences();

    // 修改点击建议项的处理，添加更多日志
    $(document).on('click', '.suggestion-item', function(e) {
        e.stopPropagation();
        let selectedValue = $(this).text();
        let suggestionList = $(this).closest('.suggestion-list');
        let input = suggestionList.siblings('input');
        
        console.log('选择建议项:', selectedValue);
        
        if (input.length > 0) {
            input.val(selectedValue);
            suggestionList.remove();

            // 如果是 level2 输入框，检查并自动填充 level1
            if (input.hasClass('level2-input')) {
                let level1Input = input.closest('.entity-input').find('.level1-input');
                console.log('当前level1值:', level1Input.val());
                
                if (!level1Input.val()) {
                    console.log('尝试查找匹配的level1值');
                    let lastLevel1 = findLastLevel1ForLevel2(selectedValue);
                    if (lastLevel1) {
                        console.log('找到匹配的level1值，正在填充:', lastLevel1);
                        level1Input.val(lastLevel1);
                    }
                }
            }

            debouncedSave();
        }
    });

    // 修改点击输入框的处理
    $(document).on('click', '.level2-input, .status-input', function(e) {
        e.stopPropagation(); // 阻止事件冒泡
        $('.suggestion-list').remove(); // 先移除所有已存在的建议列表
        
        if ($(this).hasClass('level2-input')) {
            filterSuggestions($(this), Array.from(usedLevel2Values), $(this).val());
        } else if ($(this).hasClass('status-input')) {
            let level2Value = $(this).closest('.entity-input').find('.level2-input').val();
            if (level2Value && level2Value.trim() !== '') {
                let relevantStatuses = getStatusesByLevel2(level2Value);
                if (relevantStatuses.length > 0) {
                    filterSuggestions($(this), relevantStatuses, $(this).val());
                }
            }
        }
    });

    // 修改文档点击事件，处理建议列表的隐藏
    $(document).on('click', function(e) {
        if (!$(e.target).closest('.field-container').length) {
            $('.suggestion-list').remove();
        }
    });

    // 点击 level2 输入框时显示所有建议
    $(document).on('click', '.level2-input', function() {
        $('.level2-input, .status-input').removeData('showing-suggestions');
        $(this).data('showing-suggestions', true);
        filterSuggestions($(this), Array.from(usedLevel2Values), '');
    });

    // 点击 status 输入框时显示相关建议
    $(document).on('click', '.status-input', function() {
        $('.level2-input, .status-input').removeData('showing-suggestions');
        $(this).data('showing-suggestions', true);
        
        let level2Value = $(this).closest('.entity-input').find('.level2-input').val();
        console.log('当前行的level2值:', level2Value);
        
        if (level2Value && level2Value.trim() !== '') {
            let relevantStatuses = getStatusesByLevel2(level2Value);
            if (relevantStatuses.length > 0) {
                filterSuggestions($(this), relevantStatuses, '');
            }
        }
    });

    // 修改创建实体输入表单的函数
    function createEntityInput(entity = {}, index) {
        const hasDoubt = entity.doubt_remark && entity.doubt_remark.trim() !== '';
        
        return `
            <div class="entity-input" data-index="${index}">
                <button class="remove-entity-btn" title="删除此实体">×</button>
                
                <div class="field-container">
                    <div class="field-label">当前行业</div>
                    <input type="text" value="${entity.industry || ''}" 
                           placeholder="输入行业" 
                           class="industry-input" />
                </div>

                <div class="field-container">
                    <div class="field-label">一级分类</div>
                    <select class="level1-input" required>
                        <option value="">请选择</option>
                        ${createSelectOptions(LEVEL1_OPTIONS, entity.level1)}
                    </select>
                </div>

                <div class="field-container">
                    <div class="field-label">二级分类</div>
                    <input type="text" value="${entity.level2 || ''}" placeholder="输入二级分类" class="level2-input" />
                </div>

                <div class="field-container">
                    <div class="field-label">时间属性</div>
                    <select class="time-attr-input" required>
                        <option value="">请选择</option>
                        ${createSelectOptions(TIME_ATTR_OPTIONS, entity.time_attr)}
                    </select>
                </div>

                <div class="field-container">
                    <div class="field-label">状态</div>
                    <input type="text" value="${entity.status || ''}" placeholder="输入状态" class="status-input" />
                </div>

                <div class="field-container">
                    <div class="field-label">分数</div>
                    <select class="score-input" required>
                        <option value="">请选择</option>
                        ${createSelectOptions(SCORE_OPTIONS, entity.score)}
                    </select>
                </div>

                <div class="field-container ${hasDoubt ? 'has-doubt' : ''}">
                    <div class="field-label">存疑备注</div>
                    <input type="text" value="${entity.doubt_remark || ''}" 
                           placeholder="输入备注" 
                           class="doubt-input" />
                </div>
            </div>
        `;
    }

    // 修改添加新实体的处理函数
    $(document).on('click', '.add-entity-btn', function() {
        let entityForm = $(this).closest('.entity-form');
        let newIndex = entityForm.find('.entity-input').length;
        
        // 创建新的实体输入表单
        let newEntity = $(createEntityInput({}, newIndex));
        
        // 在第一个实体之前插入新实体（如果存在其他实体）
        let firstEntity = entityForm.find('.entity-input').first();
        if (firstEntity.length > 0) {
            firstEntity.before(newEntity);
        } else {
            // 如果没有其他实体，就插入到添加按钮之前
            $(this).parent().before(newEntity);
        }
        
        // 重新编号所有实体
        entityForm.find('.entity-input').each(function(index) {
            $(this).attr('data-index', index);
        });
        
        debouncedSave();
    });

    // 删除实体的处理函数
    $(document).on('click', '.remove-entity-btn', function() {
        let entityForm = $(this).closest('.entity-form');
        let entityInputs = entityForm.find('.entity-input');
        
        if (entityInputs.length > 1) {  // 确保至少保留一个实体输入表单
            $(this).closest('.entity-input').remove();
            // 重新编号
            entityForm.find('.entity-input').each(function(index) {
                $(this).attr('data-index', index);
            });
            debouncedSave();
        }
    });

    // 添加一个新函数来查找最近使用的行业值
    function findLastIndustry() {
        // 先在当前表单中查找
        let currentForm = $('.entity-form.active');
        let currentInputs = currentForm.find('.entity-input');
        
        // 从当前行向上查找
        for (let i = currentInputs.length - 1; i >= 0; i--) {
            let industry = currentInputs.eq(i).find('.industry-input').val();
            if (industry && industry.trim() !== '') {
                return industry;
            }
        }

        // 如果当前表单中没找到，查找历史数据
        for (let i = allEntities.length - 1; i >= 0; i--) {
            let sentence = allEntities[i];
            if (sentence && sentence.entities) {
                for (let j = sentence.entities.length - 1; j >= 0; j--) {
                    let entity = sentence.entities[j];
                    if (entity.industry && entity.industry.trim() !== '') {
                        return entity.industry;
                    }
                }
            }
        }
        
        return null;
    }

    // 修改自动填充行业的函数，添加日志以便调试
    function autoFillIndustry(inputContainer) {
        let industryInput = inputContainer.find('.industry-input');
        // 只在行业字段为空时自动填充
        if (!industryInput.val() || industryInput.val().trim() === '') {
            let lastIndustry = findLastIndustry();
            console.log('找到的上一个行业值:', lastIndustry);
            if (lastIndustry) {
                industryInput.val(lastIndustry);
                console.log('已自动填充行业:', lastIndustry);
                debouncedSave();
            }
        }
    }

    // 修改事件处理，添加 industry-input 的输入事件监听
    $(document).on('input', '.industry-input, .level2-input, .status-input, .doubt-input', function() {
        let inputContainer = $(this).closest('.entity-input');
        // 只有当不是 industry-input 在输入时才自动填充行业
        if (!$(this).hasClass('industry-input')) {
            autoFillIndustry(inputContainer);
        }
        debouncedSave();
    });

    $(document).on('change', '.level1-input, .time-attr-input, .score-input', function() {
        let inputContainer = $(this).closest('.entity-input');
        autoFillIndustry(inputContainer);
        debouncedSave();
    });

    // 添加存疑备注输入框的实时监听
    $(document).on('input', '.doubt-input', function() {
        const fieldContainer = $(this).closest('.field-container');
        const hasDoubt = $(this).val().trim() !== '';
        
        // 更新高亮状态
        if (hasDoubt) {
            fieldContainer.addClass('has-doubt');
        } else {
            fieldContainer.removeClass('has-doubt');
        }
        
        debouncedSave();
    });

    // 修改事件监听，区分实时保存和完成保存
    $(document).on('input', '.level2-input, .status-input', function() {
        // 输入时只显示建议，不保存
        let keyword = $(this).val();
        if ($(this).hasClass('level2-input')) {
            filterSuggestions($(this), Array.from(usedLevel2Values), keyword);
        } else if ($(this).hasClass('status-input')) {
            let level2Value = $(this).closest('.entity-input').find('.level2-input').val();
            if (level2Value) {
                let relevantStatuses = getStatusesByLevel2(level2Value);
                filterSuggestions($(this), relevantStatuses, keyword);
            }
        }
    });

    // 添加失去焦点事件，在输入完成时保存和更新推荐列表
    $(document).on('blur', '.level2-input, .status-input', function() {
        let value = $(this).val().trim();
        if (value) {  // 只有当值不为空时才保存和更新推荐
            if ($(this).hasClass('level2-input')) {
                usedLevel2Values.add(value);
            }
            debouncedSave();
        }
    });

    // 修改输入事件的保存逻辑
    $(document).on('input', '.level2-input', function() {
        let keyword = $(this).val();
        let level1Input = $(this).closest('.entity-input').find('.level1-input');
        
        // 只在输入框内容变化时更新建议
        if (keyword) {
            filterSuggestions($(this), Array.from(usedLevel2Values), keyword);
        }

        // 只有在输入完成后才保存
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => {
            if (!level1Input.val()) {
                let lastLevel1 = findLastLevel1ForLevel2(keyword);
                if (lastLevel1) {
                    level1Input.val(lastLevel1);
                }
            }
            debouncedSave();
        }, 500);  // 500毫秒后保存
    });

    // 其他输入框（如行业、一级分类等）保持实时保存
    $(document).on('input', '.industry-input, .level1-input, .time-attr-input, .score-input, .doubt-input', function() {
        debouncedSave();
    });
});
